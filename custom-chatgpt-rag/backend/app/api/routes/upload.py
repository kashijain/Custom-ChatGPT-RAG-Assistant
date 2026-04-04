from fastapi import APIRouter, Depends, File, UploadFile

from app.core.config import Settings, get_settings
from app.core.dependencies import get_rag_service
from app.models.schemas import UploadResponse
from app.services.rag_service import RAGService


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    document_id, filename, chunks_indexed = await rag_service.ingest_pdf(
        file=file,
        max_upload_size_bytes=settings.max_upload_size_mb * 1024 * 1024,
    )

    return UploadResponse(
        document_id=document_id,
        filename=filename,
        chunks_indexed=chunks_indexed,
        message="PDF uploaded, processed, and indexed successfully.",
    )
