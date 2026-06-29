"""
Adaptateur ChromaDB — écriture des chunks vectorisés.

Contrat partagé avec intrabot-search :
  - collection : nom configurable (`COLLECTION_NAME`, défaut `intrabot`)
  - espace     : cosine
  - metadata   : `source` (nom fichier), `chunk_index`, `headings` (optionnel)
"""

import uuid

import chromadb

from app.domain.model import Chunk
from app.domain.ports import VectorStore


class ChromaStore(VectorStore):
    """Persistance locale des embeddings via ChromaDB PersistentClient."""

    def __init__(self, persist_path: str, collection_name: str) -> None:
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.collection.add(
            ids=[str(uuid.uuid4()) for _ in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
        )

    def count(self) -> int:
        return self.collection.count()

    def list_sources(self) -> dict[str, int]:
        if self.collection.count() == 0:
            return {}

        result = self.collection.get(include=["metadatas"])
        counts: dict[str, int] = {}
        for metadata in result["metadatas"]:
            if not metadata:
                continue
            source = metadata.get("source", "unknown")
            counts[source] = counts.get(source, 0) + 1
        return counts

    def get_indexed_categories(self) -> dict[str, str]:
        if self.collection.count() == 0:
            return {}

        result = self.collection.get(include=["metadatas"])
        categories: dict[str, str] = {}
        for metadata in result["metadatas"]:
            if not metadata:
                continue
            source = metadata.get("source")
            if not source or source in categories:
                continue
            categories[source] = metadata.get("category", "public")
        return categories

    def delete_by_source(self, source: str) -> int:
        result = self.collection.get(where={"source": source}, include=[])
        chunk_ids = result["ids"]
        if not chunk_ids:
            return 0
        self.collection.delete(ids=chunk_ids)
        return len(chunk_ids)
