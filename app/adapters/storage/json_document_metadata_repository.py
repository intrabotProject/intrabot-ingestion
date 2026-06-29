"""Registre JSON des métadonnées documentaires (catégorie d'accès par fichier)."""

import json
from pathlib import Path

from app.domain.access import DEFAULT_DOCUMENT_CATEGORY, DocumentCategory, normalize_category
from app.domain.ports import DocumentMetadataRepository


class JsonDocumentMetadataRepository(DocumentMetadataRepository):
    """Persiste source → category dans un fichier JSON à côté du corpus."""

    def __init__(self, registry_path: str) -> None:
        self._path = Path(registry_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("{}", encoding="utf-8")

    def get_category(self, source: str) -> DocumentCategory:
        data = self._read()
        raw = data.get(source, DEFAULT_DOCUMENT_CATEGORY)
        try:
            return normalize_category(raw)
        except ValueError:
            return DEFAULT_DOCUMENT_CATEGORY

    def set_category(self, source: str, category: str) -> DocumentCategory:
        normalized = normalize_category(category)
        data = self._read()
        data[source] = normalized
        self._write(data)
        return normalized

    def delete(self, source: str) -> None:
        data = self._read()
        if source in data:
            del data[source]
            self._write(data)

    def list_all(self) -> dict[str, DocumentCategory]:
        data = self._read()
        result: dict[str, DocumentCategory] = {}
        for source, raw in data.items():
            try:
                result[source] = normalize_category(raw)
            except ValueError:
                result[source] = DEFAULT_DOCUMENT_CATEGORY
        return result

    def _read(self) -> dict[str, str]:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, data: dict[str, str]) -> None:
        self._path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
