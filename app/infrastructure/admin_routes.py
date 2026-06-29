"""Routes d'administration documentaire (upload, indexation, statistiques)."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.application.admin_service import AdminService
from app.domain.access import CATEGORY_LABELS, DEFAULT_DOCUMENT_CATEGORY, DOCUMENT_CATEGORIES
from app.domain.model import DocumentNotFoundError, UnsupportedFileTypeError
from app.infrastructure.dependencies import get_admin_service
from app.infrastructure.schemas import (
    CategoryInfoSchema,
    CollectionStatsSchema,
    DeleteDocumentResponseSchema,
    DocumentSummarySchema,
    ReindexDocumentResponseSchema,
    UpdateDocumentCategorySchema,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/categories", response_model=list[CategoryInfoSchema])
def list_categories() -> list[CategoryInfoSchema]:
    return [
        CategoryInfoSchema(id=category, label=CATEGORY_LABELS[category])
        for category in DOCUMENT_CATEGORIES
    ]


@router.get("/documents", response_model=list[DocumentSummarySchema])
def list_documents(
    service: AdminService = Depends(get_admin_service),
) -> list[DocumentSummarySchema]:
    return [
        DocumentSummarySchema.model_validate(document)
        for document in service.list_documents()
    ]


@router.post("/documents/upload", response_model=DocumentSummarySchema)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default=DEFAULT_DOCUMENT_CATEGORY),
    service: AdminService = Depends(get_admin_service),
) -> DocumentSummarySchema:
    """Enregistre le fichier et l'ingère immédiatement dans ChromaDB."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    try:
        content = await file.read()
        document = service.upload_document(
            filename=file.filename,
            content=content,
            category=category,
        )
        return DocumentSummarySchema.model_validate(document)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/documents/{source}/category", response_model=DocumentSummarySchema)
def update_document_category(
    source: str,
    body: UpdateDocumentCategorySchema,
    service: AdminService = Depends(get_admin_service),
) -> DocumentSummarySchema:
    try:
        document = service.update_document_category(source, body.category)
        return DocumentSummarySchema.model_validate(document)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/documents/{source}", response_model=DeleteDocumentResponseSchema)
def delete_document(
    source: str,
    service: AdminService = Depends(get_admin_service),
) -> DeleteDocumentResponseSchema:
    try:
        result = service.delete_document(source)
        return DeleteDocumentResponseSchema.model_validate(result)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/documents/{source}/reindex",
    response_model=ReindexDocumentResponseSchema,
)
def reindex_document(
    source: str,
    service: AdminService = Depends(get_admin_service),
) -> ReindexDocumentResponseSchema:
    try:
        result = service.reindex_document(source)
        return ReindexDocumentResponseSchema.model_validate(result)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/collection/stats", response_model=CollectionStatsSchema)
def collection_stats(
    service: AdminService = Depends(get_admin_service),
) -> CollectionStatsSchema:
    return CollectionStatsSchema.model_validate(service.get_collection_stats())
