from abc import ABC, abstractmethod
from app.domain.model import Document, Chunk


class DocumentLoader(ABC):
    @abstractmethod
    def load(self) -> list[Document]:
        """Retourne la liste des documents à ingérer."""
        ...


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, document: Document) -> str:
        """Parse un document et retourne son texte brut."""
        ...


class DocumentChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, source: str) -> list[Chunk]:
        """Découpe un texte en chunks enrichis de métadonnées."""
        ...


class Embedder(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Vectorise une liste de chunks à indexer."""
        ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Vectorise une question utilisateur."""
        ...


class VectorStore(ABC):
    @abstractmethod
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Stocke les chunks et leurs vecteurs."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Retourne le nombre de chunks indexés."""
        ...