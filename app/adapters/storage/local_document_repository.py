"""Stockage local des documents uploadés dans `SOURCE_DIR`."""

import os
from pathlib import Path

from app.adapters.loader.local_loader import LocalLoader
from app.domain.model import Document, UnsupportedFileTypeError
from app.domain.ports import DocumentRepository


class LocalDocumentRepository(DocumentRepository):
    """Persiste les fichiers uploadés sur le disque, avec validation du nom et du type."""

    def __init__(self, source_dir: str) -> None:
        self._source_dir = Path(source_dir)
        self._source_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        safe_name = self._safe_filename(filename)
        if Path(safe_name).suffix.lower() not in LocalLoader.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(safe_name)

        target_path = self._source_dir / safe_name
        target_path.write_bytes(content)
        return safe_name

    def delete(self, source: str) -> bool:
        safe_name = self._safe_filename(source)
        target_path = self._source_dir / safe_name
        if not target_path.is_file():
            return False
        target_path.unlink()
        return True

    def get_document(self, source: str) -> Document | None:
        safe_name = self._safe_filename(source)
        target_path = self._source_dir / safe_name
        if not target_path.is_file():
            return None
        if target_path.suffix.lower() not in LocalLoader.SUPPORTED_EXTENSIONS:
            return None
        return Document(name=safe_name, path=str(target_path.resolve()))

    @staticmethod
    def _safe_filename(filename: str) -> str:
        """Empêche les chemins relatifs (`../`) et les noms vides."""
        name = os.path.basename(filename.strip())
        if not name or name in {".", ".."}:
            raise ValueError("Invalid filename")
        return name
