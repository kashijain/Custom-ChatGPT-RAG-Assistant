from functools import lru_cache

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.vector_store import FAISSVectorStore


@lru_cache
def get_rag_service() -> RAGService:
    settings = get_settings()
    embedding_service = EmbeddingService(
        api_base_url=settings.api_base_url,
        api_key=settings.api_key,
        model=settings.embedding_model,
    )
    llm_service = LLMService(
        api_base_url=settings.api_base_url,
        api_key=settings.api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
    )
    vector_store = FAISSVectorStore(
        index_path=settings.faiss_index_path,
        metadata_path=settings.faiss_metadata_path,
    )

    return RAGService(
        embedding_service=embedding_service,
        llm_service=llm_service,
        vector_store=vector_store,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        retrieval_top_k=settings.retrieval_top_k,
        upload_dir=settings.upload_dir,
    )
