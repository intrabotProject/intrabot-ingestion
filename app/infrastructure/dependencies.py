"""
Composition root — instancie les adaptateurs et services applicatifs.

Toute dépendance concrète (Cohere, Docling, Chroma) est câblée ici,
jamais dans le domaine ni dans les services métier.
"""

from functools import lru_cache

from app.adapters.chunker.docling_chunker import DoclingChunker
from app.adapters.embedder.cohere_embedder import CohereEmbedder
from app.adapters.loader.local_loader import LocalLoader
from app.adapters.parser.docling_parser import DoclingParser
from app.adapters.storage.json_document_metadata_repository import (
    JsonDocumentMetadataRepository,
)
from app.adapters.storage.json_staging_registry import JsonStagingRegistry
from app.adapters.storage.local_document_repository import LocalDocumentRepository
from app.adapters.storage.local_staging_repository import LocalStagingRepository
from app.adapters.vectorstore.chroma_store import ChromaStore
from app.application.admin_service import AdminService
from app.application.ingestion_service import IngestionService
from app.application.staging_service import StagingService
from app.domain.ports import Embedder, VectorStore
from app.infrastructure.config import settings


def get_embedder() -> Embedder:
    return CohereEmbedder(api_key=settings.cohere_api_key)


@lru_cache
def get_vector_store() -> ChromaStore:
    return ChromaStore(
        persist_path=settings.chroma_path,
        collection_name=settings.collection_name,
    )


def get_document_repository() -> LocalDocumentRepository:
    return LocalDocumentRepository(source_dir=settings.source_dir)


def get_metadata_repository() -> JsonDocumentMetadataRepository:
    return JsonDocumentMetadataRepository(registry_path=settings.metadata_registry_path)


def get_ingestion_service() -> IngestionService:
    return IngestionService(
        loader=LocalLoader(local_dir=settings.source_dir),
        parser=DoclingParser(),
        chunker=DoclingChunker(max_tokens=settings.max_tokens),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
        metadata_repository=get_metadata_repository(),
    )


def get_admin_service() -> AdminService:
    return AdminService(
        loader=LocalLoader(local_dir=settings.source_dir),
        vector_store=get_vector_store(),
        collection_name=settings.collection_name,
        document_repository=get_document_repository(),
        metadata_repository=get_metadata_repository(),
        ingestion_service=get_ingestion_service(),
    )


def get_staging_service() -> StagingService:
    return StagingService(
        staging_repository=LocalStagingRepository(
            staging_dir=settings.staging_dir,
            docs_dir=settings.source_dir,
        ),
        staging_registry=JsonStagingRegistry(registry_path=settings.staging_registry_path),
        metadata_repository=get_metadata_repository(),
        vector_store=get_vector_store(),
        ingestion_service=get_ingestion_service(),
    )
