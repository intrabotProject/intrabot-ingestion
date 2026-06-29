FROM python:3.11-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /app/data/docs /app/data/chroma

ENV SOURCE_DIR=/app/data/docs \
    CHROMA_PATH=/app/data/chroma \
    METADATA_REGISTRY_PATH=/app/data/document_registry.json \
    COLLECTION_NAME=intrabot \
    ONNXRUNTIME_DISABLE_CPU_AFFINITY=1

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "app.infrastructure.api:app", "--host", "0.0.0.0", "--port", "8001"]
