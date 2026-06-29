"""
Service applicatif d'administration documentaire.

Fusionne l'état disque (`data/docs/`), le registre de catégories et l'index
ChromaDB pour exposer le corpus, gérer les uploads et déclencher la réindexation.
"""

from pathlib import Path

from app.application.ingestion_service import IngestionService
from app.domain.access import DEFAULT_DOCUMENT_CATEGORY, normalize_category
from app.domain.model import (
    CollectionStats,
    DeleteDocumentResult,
    Document,
    DocumentNotFoundError,
    DocumentSummary,
    ReindexDocumentResult,
)
from app.domain.ports import DocumentLoader, DocumentMetadataRepository, DocumentRepository, VectorStore


class AdminService:
    """Orchestre les opérations CRUD sur les documents et leur index vectoriel."""

    def __init__(
        self,
        loader: DocumentLoader,
        vector_store: VectorStore,
        collection_name: str,
        document_repository: DocumentRepository,
        metadata_repository: DocumentMetadataRepository,
        ingestion_service: IngestionService,
    ) -> None:
        self._loader = loader
        self._vector_store = vector_store
        self._collection_name = collection_name
        self._document_repository = document_repository
        self._metadata_repository = metadata_repository
        self._ingestion_service = ingestion_service

    def list_documents(self) -> list[DocumentSummary]:
        indexed_sources = self._vector_store.list_sources()
        indexed_categories = self._vector_store.get_indexed_categories()
        registry_categories = self._metadata_repository.list_all()
        disk_documents = self._load_disk_documents()
        all_sources = set(indexed_sources) | set(disk_documents) | set(registry_categories)

        summaries: list[DocumentSummary] = []
        for source in sorted(all_sources):
            chunk_count = indexed_sources.get(source, 0)
            disk_doc = disk_documents.get(source)
            category = (
                registry_categories.get(source)
                or indexed_categories.get(source)
                or DEFAULT_DOCUMENT_CATEGORY
            )
            summaries.append(
                DocumentSummary(
                    source=source,
                    chunk_count=chunk_count,
                    status="indexed" if chunk_count > 0 else "pending",
                    category=category,
                    file_size_bytes=self._file_size_bytes(disk_doc),
                )
            )

        return summaries

    def get_collection_stats(self) -> CollectionStats:
        documents = self.list_documents()
        indexed_count = sum(1 for doc in documents if doc.status == "indexed")
        pending_count = sum(1 for doc in documents if doc.status == "pending")

        return CollectionStats(
            collection_name=self._collection_name,
            document_count=len(documents),
            chunk_count=self._vector_store.count(),
            indexed_document_count=indexed_count,
            pending_document_count=pending_count,
        )

    def upload_document(
        self,
        filename: str,
        content: bytes,
        category: str = DEFAULT_DOCUMENT_CATEGORY,
    ) -> DocumentSummary:
        """Enregistre le fichier sur disque puis l'ingère immédiatement dans ChromaDB."""
        normalized_category = normalize_category(category)
        saved_name = self._document_repository.save(filename, content)
        self._metadata_repository.set_category(saved_name, normalized_category)

        document = self._document_repository.get_document(saved_name)
        if document is None:
            raise ValueError(f"Failed to save document: {filename}")

        self._vector_store.delete_by_source(saved_name)
        ingest_result = self._ingestion_service.ingest_document(
            document,
            category=normalized_category,
        )
        chunks_indexed = ingest_result["chunks_indexed"]

        return DocumentSummary(
            source=saved_name,
            chunk_count=chunks_indexed,
            status="indexed" if chunks_indexed > 0 else "pending",
            category=normalized_category,
            file_size_bytes=self._file_size_bytes(document),
        )

    def update_document_category(self, source: str, category: str) -> DocumentSummary:
        """Change la catégorie d'accès et réindexe le document si présent sur disque."""
        document = self._document_repository.get_document(source)
        if document is None and source not in self._vector_store.list_sources():
            raise DocumentNotFoundError(source)

        normalized_category = self._metadata_repository.set_category(source, category)

        if document is None:
            return DocumentSummary(
                source=source,
                chunk_count=self._vector_store.list_sources().get(source, 0),
                status="indexed",
                category=normalized_category,
                file_size_bytes=None,
            )

        self._vector_store.delete_by_source(source)
        ingest_result = self._ingestion_service.ingest_document(
            document,
            category=normalized_category,
        )
        chunks_indexed = ingest_result["chunks_indexed"]

        return DocumentSummary(
            source=source,
            chunk_count=chunks_indexed,
            status="indexed" if chunks_indexed > 0 else "pending",
            category=normalized_category,
            file_size_bytes=self._file_size_bytes(document),
        )

    def delete_document(self, source: str) -> DeleteDocumentResult:
        chunks_deleted = self._vector_store.delete_by_source(source)
        file_deleted = self._document_repository.delete(source)
        self._metadata_repository.delete(source)

        if not file_deleted and chunks_deleted == 0:
            raise DocumentNotFoundError(source)

        return DeleteDocumentResult(
            source=source,
            file_deleted=file_deleted,
            chunks_deleted=chunks_deleted,
        )

    def reindex_document(self, source: str) -> ReindexDocumentResult:
        document = self._document_repository.get_document(source)
        if document is None:
            raise DocumentNotFoundError(source)

        category = self._metadata_repository.get_category(source)
        self._vector_store.delete_by_source(source)
        ingest_result = self._ingestion_service.ingest_document(
            document,
            category=category,
        )

        return ReindexDocumentResult(
            source=source,
            chunks_indexed=ingest_result["chunks_indexed"],
            total_in_collection=self._vector_store.count(),
        )

    def _load_disk_documents(self) -> dict[str, Document]:
        try:
            documents = self._loader.load()
        except FileNotFoundError:
            return {}

        return {document.name: document for document in documents}

    @staticmethod
    def _file_size_bytes(document: Document | None) -> int | None:
        if document is None:
            return None
        return Path(document.path).stat().st_size
