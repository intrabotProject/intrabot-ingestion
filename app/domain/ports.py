from abc import ABC, abstractmethod
from app.domain.model import Document, Chunk


class DocumentLoader(ABC):
    @abstractmethod
    def load(self) -> list[Document]:
        """Retourne la liste des documents à ingérer."""
        ...


class DocumentMetadataRepository(ABC):
    @abstractmethod
    def get_category(self, source: str) -> str:
        """Retourne la catégorie d'accès d'un document."""
        ...

    @abstractmethod
    def set_category(self, source: str, category: str) -> str:
        """Enregistre la catégorie et retourne la valeur normalisée."""
        ...

    @abstractmethod
    def delete(self, source: str) -> None:
        """Supprime les métadonnées d'un document."""
        ...

    @abstractmethod
    def list_all(self) -> dict[str, str]:
        """Retourne toutes les catégories connues (source → category)."""
        ...


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, filename: str, content: bytes) -> str:
        """Enregistre un fichier uploadé et retourne son nom."""
        ...

    @abstractmethod
    def delete(self, source: str) -> bool:
        """Supprime un fichier du stockage. Retourne True s'il existait."""
        ...

    @abstractmethod
    def get_document(self, source: str) -> Document | None:
        """Retourne le document s'il est présent sur disque."""
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

    @abstractmethod
    def list_sources(self) -> dict[str, int]:
        """Retourne le nombre de chunks indexés par nom de source."""
        ...

    @abstractmethod
    def get_indexed_categories(self) -> dict[str, str]:
        """Retourne la catégorie indexée par source (premier chunk trouvé)."""
        ...

    @abstractmethod
    def delete_by_source(self, source: str) -> int:
        """Supprime tous les chunks d'une source. Retourne le nombre supprimé."""
        ...