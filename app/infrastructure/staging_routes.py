"""Routes de gestion des soumissions utilisateurs (zone de staging)."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.application.staging_service import StagingService
from app.domain.access import DEFAULT_DOCUMENT_CATEGORY
from app.domain.model import StagingDocumentNotFoundError, UnsupportedFileTypeError
from app.infrastructure.dependencies import get_staging_service
from app.infrastructure.schemas import (
    DocumentSummarySchema,
    RejectStagingResponseSchema,
    StagingCountSchema,
    StagingDocumentSummarySchema,
)

router = APIRouter(prefix="/staging", tags=["staging"])


@router.post("/submit", response_model=StagingDocumentSummarySchema)
async def submit_document(
    file: UploadFile = File(...),
    category: str = Form(default=DEFAULT_DOCUMENT_CATEGORY),
    submitted_by: str = Form(default="anonymous"),
    service: StagingService = Depends(get_staging_service),
) -> StagingDocumentSummarySchema:
    """Enregistre un fichier en zone de staging (soumis par un utilisateur)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    try:
        content = await file.read()
        result = service.submit(
            filename=file.filename,
            content=content,
            category=category,
            submitted_by=submitted_by,
        )
        return StagingDocumentSummarySchema.model_validate(result)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[StagingDocumentSummarySchema])
def list_pending(
    service: StagingService = Depends(get_staging_service),
) -> list[StagingDocumentSummarySchema]:
    """Liste tous les documents en attente de validation admin."""
    return [
        StagingDocumentSummarySchema.model_validate(doc)
        for doc in service.list_pending()
    ]


@router.get("/count", response_model=StagingCountSchema)
def count_pending(
    service: StagingService = Depends(get_staging_service),
) -> StagingCountSchema:
    """Retourne le nombre de documents en attente (pour le badge admin)."""
    return StagingCountSchema(count=service.count_pending())


@router.post("/{source}/approve", response_model=DocumentSummarySchema)
def approve_document(
    source: str,
    service: StagingService = Depends(get_staging_service),
) -> DocumentSummarySchema:
    """Valide une soumission : indexe le document et le rend disponible dans le chatbot."""
    try:
        result = service.approve(source)
        return DocumentSummarySchema.model_validate(result)
    except StagingDocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{source}", response_model=RejectStagingResponseSchema)
def reject_document(
    source: str,
    service: StagingService = Depends(get_staging_service),
) -> RejectStagingResponseSchema:
    """Rejette une soumission : supprime le fichier sans l'indexer."""
    try:
        service.reject(source)
        return RejectStagingResponseSchema(source=source, rejected=True)
    except StagingDocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
