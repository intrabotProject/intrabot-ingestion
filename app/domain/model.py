"""
Entités et exceptions du domaine ingestion.

Aucune dépendance externe : ces types sont le contrat métier partagé
entre les services applicatifs et les adaptateurs.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Document:
    """Fichier source à ingérer (nom affiché + chemin absolu sur disque)."""

    name: str
    path: str


@dataclass
class Chunk:
    """Segment de texte indexable avec métadonnées ChromaDB."""

    text: str
    metadata: dict = field(default_factory=dict)
    # Exemple de metadata : {"source": "rapport.pdf", "chunk_index": 3, "headings": "..."}


@dataclass
class DocumentSummary:
    """Vue synthétique d'un document pour l'interface admin."""

    source: str
    chunk_count: int
    status: Literal["indexed", "pending"]
    category: str = "public"
    file_size_bytes: int | None = None


@dataclass
class CollectionStats:
    """Statistiques globales de la collection vectorielle."""

    collection_name: str
    document_count: int
    chunk_count: int
    indexed_document_count: int
    pending_document_count: int


@dataclass
class DeleteDocumentResult:
    source: str
    file_deleted: bool
    chunks_deleted: int


@dataclass
class ReindexDocumentResult:
    source: str
    chunks_indexed: int
    total_in_collection: int


@dataclass
class StagingDocumentSummary:
    """Vue synthétique d'un document en attente de validation admin."""

    source: str
    submitted_by: str
    submitted_at: str
    category: str
    file_size_bytes: int | None = None


class DocumentNotFoundError(Exception):
    def __init__(self, source: str):
        self.source = source
        super().__init__(f"Document not found: {source}")


class StagingDocumentNotFoundError(Exception):
    def __init__(self, source: str):
        self.source = source
        super().__init__(f"Staging document not found: {source}")


class UnsupportedFileTypeError(Exception):
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Unsupported file type: {filename}")
