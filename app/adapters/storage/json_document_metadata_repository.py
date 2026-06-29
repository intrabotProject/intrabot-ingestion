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

    def _get_entry(self, data: dict, source: str) -> dict:
        """Normalise une entrée : ancien format string → nouveau format dict."""
        entry = data.get(source, {})
        if isinstance(entry, str):
            return {"category": entry, "hash": None}
        return entry if isinstance(entry, dict) else {}

    def get_category(self, source: str) -> DocumentCategory:
        data = self._read()
        entry = self._get_entry(data, source)
        raw = entry.get("category", DEFAULT_DOCUMENT_CATEGORY)
        try:
            return normalize_category(raw)
        except ValueError:
            return DEFAULT_DOCUMENT_CATEGORY

    def set_category(self, source: str, category: str) -> DocumentCategory:
        normalized = normalize_category(category)
        data = self._read()
        entry = self._get_entry(data, source)
        entry["category"] = normalized
        data[source] = entry
        self._write(data)
        return normalized

    def get_hash(self, source: str) -> str | None:
        data = self._read()
        entry = self._get_entry(data, source)
        return entry.get("hash")

    def set_hash(self, source: str, file_hash: str) -> None:
        data = self._read()
        entry = self._get_entry(data, source)
        entry["hash"] = file_hash
        data[source] = entry
        self._write(data)

    def delete(self, source: str) -> None:
        data = self._read()
        if source in data:
            del data[source]
            self._write(data)

    def list_all(self) -> dict[str, DocumentCategory]:
        data = self._read()
        result: dict[str, DocumentCategory] = {}
        for source in data:
            entry = self._get_entry(data, source)
            raw = entry.get("category", DEFAULT_DOCUMENT_CATEGORY)
            try:
                result[source] = normalize_category(raw)
            except ValueError:
                result[source] = DEFAULT_DOCUMENT_CATEGORY
        return result

    def _read(self) -> dict:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, data: dict) -> None:
        self._path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
