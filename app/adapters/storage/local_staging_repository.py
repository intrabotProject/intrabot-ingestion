"""Stockage local des fichiers soumis par les utilisateurs (zone de staging)."""

import os
from pathlib import Path

from app.adapters.loader.local_loader import LocalLoader
from app.domain.model import Document, StagingDocumentNotFoundError, UnsupportedFileTypeError
from app.domain.ports import StagingDocumentRepository


class LocalStagingRepository(StagingDocumentRepository):
    """Persiste les fichiers en attente de validation dans `data/staging/`."""

    def __init__(self, staging_dir: str, docs_dir: str) -> None:
        self._staging_dir = Path(staging_dir)
        self._docs_dir = Path(docs_dir)
        self._staging_dir.mkdir(parents=True, exist_ok=True)
        self._docs_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        safe_name = self._safe_filename(filename)
        if Path(safe_name).suffix.lower() not in LocalLoader.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(safe_name)
        (self._staging_dir / safe_name).write_bytes(content)
        return safe_name

    def move_to_docs(self, source: str) -> Document:
        safe_name = self._safe_filename(source)
        staging_path = self._staging_dir / safe_name
        if not staging_path.is_file():
            raise StagingDocumentNotFoundError(source)
        docs_path = self._docs_dir / safe_name
        staging_path.rename(docs_path)
        return Document(name=safe_name, path=str(docs_path.resolve()))

    def delete(self, source: str) -> bool:
        safe_name = self._safe_filename(source)
        target = self._staging_dir / safe_name
        if not target.is_file():
            return False
        target.unlink()
        return True

    def get_document(self, source: str) -> Document | None:
        safe_name = self._safe_filename(source)
        target = self._staging_dir / safe_name
        if not target.is_file():
            return None
        return Document(name=safe_name, path=str(target.resolve()))

    @staticmethod
    def _safe_filename(filename: str) -> str:
        name = os.path.basename(filename.strip())
        if not name or name in {".", ".."}:
            raise ValueError("Invalid filename")
        return name
