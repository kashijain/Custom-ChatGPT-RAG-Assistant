from fastapi import APIRouter, Depends

from app.core.dependencies import get_rag_service
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import RAGService


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(
    payload: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    answer, sources = await rag_service.answer_question(
        question=payload.question,
        document_id=payload.document_id,
        top_k=payload.top_k,
    )
    return ChatResponse(answer=answer, sources=sources)
