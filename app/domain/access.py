"""Catégories d'accès documentaire et validation."""

from typing import Literal

DocumentCategory = Literal["public", "engineering", "rh", "gouvernance", "finance"]

DOCUMENT_CATEGORIES: tuple[DocumentCategory, ...] = (
    "public",
    "engineering",
    "rh",
    "gouvernance",
    "finance",
)

DEFAULT_DOCUMENT_CATEGORY: DocumentCategory = "public"

CATEGORY_LABELS: dict[DocumentCategory, str] = {
    "public": "Public (tous)",
    "engineering": "Technique / Ingénierie",
    "rh": "Ressources humaines",
    "gouvernance": "Gouvernance",
    "finance": "Finance",
}


def normalize_category(raw: str) -> DocumentCategory:
    normalized = raw.strip().lower()
    if normalized not in DOCUMENT_CATEGORIES:
        raise ValueError(
            f"Invalid category '{raw}'. "
            f"Allowed: {', '.join(DOCUMENT_CATEGORIES)}"
        )
    return normalized  # type: ignore[return-value]
