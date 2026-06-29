"""
API FastAPI du service d'ingestion.

Endpoints publics : santé, ingestion batch, embedding unitaire.
Endpoints admin : gestion du corpus via le routeur `/admin`.
"""

from fastapi import FastAPI

from app.infrastructure.admin_routes import router as admin_router
from app.infrastructure.dependencies import get_embedder, get_ingestion_service
from app.infrastructure.schemas import EmbedRequestSchema

app = FastAPI(
    title="IntraBot — Ingestion Service",
    description="Pipeline documentaire : chargement → parsing → chunking → embedding → ChromaDB.",
    version="1.0.0",
)
app.include_router(admin_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
def ingest() -> dict[str, str | int]:
    """Ingère tous les fichiers présents dans `SOURCE_DIR`."""
    service = get_ingestion_service()
    result = service.run()
    return {"status": "done", **result}


@app.post("/embed")
def embed(request: EmbedRequestSchema) -> dict[str, list[float]]:
    """Expose l'embedding d'une requête (utilisé par intrabot-search)."""
    embedder = get_embedder()
    vector = embedder.embed_query(request.text)
    return {"embedding": vector}
