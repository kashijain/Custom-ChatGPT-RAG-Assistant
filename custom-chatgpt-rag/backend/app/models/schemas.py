from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_indexed: int
    message: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    document_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=10)


class SourceSnippet(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    score: float
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
