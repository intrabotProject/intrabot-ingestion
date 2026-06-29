"""Registre JSON des documents en attente de validation (soumis par les utilisateurs)."""

import json
from pathlib import Path


class JsonStagingRegistry:
    """Persiste les métadonnées des soumissions : source → {category, submitted_by, submitted_at}."""

    def __init__(self, registry_path: str) -> None:
        self._path = Path(registry_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("{}", encoding="utf-8")

    def save(self, source: str, category: str, submitted_by: str, submitted_at: str) -> None:
        data = self._read()
        data[source] = {
            "category": category,
            "submitted_by": submitted_by,
            "submitted_at": submitted_at,
        }
        self._write(data)

    def get(self, source: str) -> dict | None:
        return self._read().get(source)

    def delete(self, source: str) -> None:
        data = self._read()
        if source in data:
            del data[source]
            self._write(data)

    def list_all(self) -> dict[str, dict]:
        return self._read()

    def count(self) -> int:
        return len(self._read())

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
