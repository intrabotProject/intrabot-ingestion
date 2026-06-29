"""Orchestration du pipeline d'ingestion documentaire."""

import hashlib

from app.domain.access import DEFAULT_DOCUMENT_CATEGORY
from app.domain.model import Document
from app.domain.ports import (
    DocumentChunker,
    DocumentLoader,
    DocumentMetadataRepository,
    DocumentParser,
    Embedder,
    VectorStore,
)


class IngestionService:
    """
    Pipeline : load → parse → chunk → embed → store.

    Dépend uniquement des ports du domaine ; les implémentations concrètes
    sont injectées via le composition root (`infrastructure/dependencies.py`).
    """

    def __init__(
        self,
        loader: DocumentLoader,
        parser: DocumentParser,
        chunker: DocumentChunker,
        embedder: Embedder,
        vector_store: VectorStore,
        metadata_repository: DocumentMetadataRepository,
    ) -> None:
        self.loader = loader
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self._metadata_repository = metadata_repository

    @staticmethod
    def _compute_file_hash(path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def run(self) -> dict[str, int]:
        """Ingère uniquement les documents nouveaux ou modifiés depuis la dernière indexation."""
        documents = self.loader.load()
        total_chunks = 0
        files_processed = 0

        for document in documents:
            current_hash = self._compute_file_hash(document.path)
            if self._metadata_repository.get_hash(document.name) == current_hash:
                continue  # fichier inchangé, on saute

            self.vector_store.delete_by_source(document.name)
            category = self._metadata_repository.get_category(document.name)
            self._metadata_repository.set_category(document.name, category)
            total_chunks += self.ingest_document(document, category=category)["chunks_indexed"]
            self._metadata_repository.set_hash(document.name, current_hash)
            files_processed += 1

        return {
            "files_processed": files_processed,
            "chunks_indexed": total_chunks,
            "total_in_collection": self.vector_store.count(),
        }

    def ingest_document(
        self,
        document: Document,
        category: str = DEFAULT_DOCUMENT_CATEGORY,
    ) -> dict[str, int]:
        """Ingère un seul document (utilisé par l'admin pour la réindexation)."""
        text = self.parser.parse(document)
        chunks = self.chunker.chunk(text=text, source=document.name)

        if not chunks:
            return {"chunks_indexed": 0}

        for chunk in chunks:
            chunk.metadata["category"] = category

        embeddings = self.embedder.embed_documents([chunk.text for chunk in chunks])
        self.vector_store.add(chunks=chunks, embeddings=embeddings)

        return {"chunks_indexed": len(chunks)}
