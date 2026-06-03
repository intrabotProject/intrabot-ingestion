from fastapi import FastAPI

from app.infrastructure.dependencies import get_ingestion_service

app = FastAPI(title="IntraBot — Ingestion Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest():
    service = get_ingestion_service()
    result = service.run()
    return {"status": "done", **result}