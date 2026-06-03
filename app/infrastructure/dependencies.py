from app.adapters.chunker.docling_chunker import DoclingChunker
from app.adapters.embedder.cohere_embedder import CohereEmbedder
from app.adapters.loader.local_loader import LocalLoader
from app.adapters.parser.docling_parser import DoclingParser
from app.adapters.vectorstore.chroma_store import ChromaStore
from app.application.ingestion_service import IngestionService
from app.infrastructure.config import settings


def get_ingestion_service() -> IngestionService:
    loader = LocalLoader(local_dir=settings.source_dir)
    parser = DoclingParser()
    chunker = DoclingChunker(max_tokens=settings.max_tokens)
    embedder = CohereEmbedder(api_key=settings.cohere_api_key)
    vector_store = ChromaStore(
        persist_path=settings.chroma_path,
        collection_name=settings.collection_name,
    )

    return IngestionService(
        loader=loader,
        parser=parser,
        chunker=chunker,
        embedder=embedder,
        vector_store=vector_store,
    )