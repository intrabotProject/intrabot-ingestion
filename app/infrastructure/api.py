from fastapi import FastAPI
from pydantic import BaseModel

from app.infrastructure.dependencies import get_embedder, get_ingestion_service

app = FastAPI(title="IntraBot — Ingestion Service")


class EmbedRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest():
    service = get_ingestion_service()
    result = service.run()
    return {"status": "done", **result}


@app.post("/embed")
def embed(request: EmbedRequest):
    embedder = get_embedder()
    vector = embedder.embed_query(request.text)
    return {"embedding": vector}