import chromadb

from app.domain.model import Chunk
from app.domain.ports import VectorStore


class ChromaStore(VectorStore):

    def __init__(self, persist_path: str, collection_name: str):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        import uuid
        self.collection.add(
            ids=[str(uuid.uuid4()) for _ in chunks],
            documents=[c.text for c in chunks],
            embeddings=embeddings,
            metadatas=[c.metadata for c in chunks],
        )

    def count(self) -> int:
        return self.collection.count()