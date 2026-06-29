"""Service applicatif de gestion des soumissions utilisateurs (zone de staging)."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from app.adapters.storage.json_staging_registry import JsonStagingRegistry
from app.domain.access import normalize_category
from app.domain.model import (
    DocumentSummary,
    StagingDocumentNotFoundError,
    StagingDocumentSummary,
)
from app.domain.ports import DocumentMetadataRepository, StagingDocumentRepository, VectorStore
from app.application.ingestion_service import IngestionService


class StagingService:
    """
    Gère le cycle de vie des documents soumis par les utilisateurs :
    soumission → validation admin → indexation (ou rejet).
    """

    def __init__(
        self,
        staging_repository: StagingDocumentRepository,
        staging_registry: JsonStagingRegistry,
        metadata_repository: DocumentMetadataRepository,
        vector_store: VectorStore,
        ingestion_service: IngestionService,
    ) -> None:
        self._staging_repository = staging_repository
        self._staging_registry = staging_registry
        self._metadata_repository = metadata_repository
        self._vector_store = vector_store
        self._ingestion_service = ingestion_service

    def submit(
        self,
        filename: str,
        content: bytes,
        category: str,
        submitted_by: str,
    ) -> StagingDocumentSummary:
        """Enregistre un fichier dans la zone de staging en attente de validation."""
        normalized_category = normalize_category(category)
        saved_name = self._staging_repository.save(filename, content)
        submitted_at = datetime.now(timezone.utc).isoformat()
        self._staging_registry.save(saved_name, normalized_category, submitted_by, submitted_at)

        document = self._staging_repository.get_document(saved_name)
        file_size = Path(document.path).stat().st_size if document else None

        return StagingDocumentSummary(
            source=saved_name,
            submitted_by=submitted_by,
            submitted_at=submitted_at,
            category=normalized_category,
            file_size_bytes=file_size,
        )

    def list_pending(self) -> list[StagingDocumentSummary]:
        """Retourne tous les documents en attente de validation."""
        registry = self._staging_registry.list_all()
        result = []
        for source, meta in registry.items():
            document = self._staging_repository.get_document(source)
            file_size = Path(document.path).stat().st_size if document else None
            result.append(StagingDocumentSummary(
                source=source,
                submitted_by=meta.get("submitted_by", "inconnu"),
                submitted_at=meta.get("submitted_at", ""),
                category=meta.get("category", "public"),
                file_size_bytes=file_size,
            ))
        return sorted(result, key=lambda d: d.submitted_at, reverse=True)

    def count_pending(self) -> int:
        """Retourne le nombre de documents en attente (pour le badge admin)."""
        return self._staging_registry.count()

    def approve(self, source: str) -> DocumentSummary:
        """
        Valide une soumission : déplace le fichier vers docs/, l'indexe
        immédiatement et enregistre le hash pour l'ingestion incrémentale.
        """
        meta = self._staging_registry.get(source)
        if meta is None:
            raise StagingDocumentNotFoundError(source)

        document = self._staging_repository.move_to_docs(source)
        self._staging_registry.delete(source)

        category = normalize_category(meta.get("category", "public"))
        self._vector_store.delete_by_source(source)
        result = self._ingestion_service.ingest_document(document, category=category)

        file_hash = hashlib.md5(Path(document.path).read_bytes()).hexdigest()
        self._metadata_repository.set_hash(source, file_hash)
        self._metadata_repository.set_category(source, category)

        chunks_indexed = result["chunks_indexed"]
        return DocumentSummary(
            source=source,
            chunk_count=chunks_indexed,
            status="indexed" if chunks_indexed > 0 else "pending",
            category=category,
            file_size_bytes=Path(document.path).stat().st_size,
        )

    def reject(self, source: str) -> None:
        """Rejette une soumission : supprime le fichier et les métadonnées de staging."""
        meta = self._staging_registry.get(source)
        if meta is None:
            raise StagingDocumentNotFoundError(source)

        self._staging_repository.delete(source)
        self._staging_registry.delete(source)
