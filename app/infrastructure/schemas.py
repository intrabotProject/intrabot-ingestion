"""
Schémas Pydantic de la couche HTTP.

Ils sérialisent les dataclasses du domaine (`app.domain.model`) vers JSON.
`from_attributes=True` permet la conversion directe depuis les objets métier.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class DocumentSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: str
    chunk_count: int
    status: Literal["indexed", "pending"]
    category: str = "public"
    file_size_bytes: int | None = None


class UpdateDocumentCategorySchema(BaseModel):
    category: str


class CategoryInfoSchema(BaseModel):
    id: str
    label: str


class CollectionStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    collection_name: str
    document_count: int
    chunk_count: int
    indexed_document_count: int
    pending_document_count: int


class DeleteDocumentResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: str
    file_deleted: bool
    chunks_deleted: int


class ReindexDocumentResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: str
    chunks_indexed: int
    total_in_collection: int


class StagingDocumentSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: str
    submitted_by: str
    submitted_at: str
    category: str
    file_size_bytes: int | None = None


class StagingCountSchema(BaseModel):
    count: int


class RejectStagingResponseSchema(BaseModel):
    source: str
    rejected: bool


class EmbedRequestSchema(BaseModel):
    text: str
