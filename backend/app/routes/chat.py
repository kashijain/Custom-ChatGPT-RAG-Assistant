from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..utils.embeddings import FALLBACK_MODE, generate_embeddings_with_mode, get_openai_client
from ..utils.faiss_index import FAISSIndex
import logging

class ChatRequest(BaseModel):
    question: str
    active_document: str | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    demo_mode: bool = False
    embedding_mode: str = "openai"

router = APIRouter()
INDEX_DIR = "faiss_index"
faiss_index = FAISSIndex(INDEX_DIR)
logger = logging.getLogger(__name__)


def _build_demo_answer(question: str, search_results: list[tuple[dict, float]], reason: str | None) -> str:
    """Create a simple grounded answer when the OpenAI chat model is unavailable."""
    snippets = [metadata["text"] for metadata, _ in search_results[:2]]
    context_preview = "\n\n".join(snippets)
    mode_line = reason or "OpenAI quota is unavailable, so the app is running in demo mode."

    return (
        f"{mode_line}\n\n"
        f"Based on the retrieved document snippets, here is the most relevant context for your question "
        f"\"{question}\":\n\n{context_preview}"
    )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer a question based on the uploaded documents using RAG.
    """
    # Refresh the index before checking availability so newly uploaded PDFs are visible immediately.
    faiss_index.refresh()

    if faiss_index.index is None or faiss_index.index.ntotal == 0:
        raise HTTPException(status_code=400, detail="No documents have been uploaded yet")
    
    try:
        # Use the same embedding mode as the active document to avoid retrieval mismatch.
        preferred_mode = faiss_index.get_embedding_mode(request.active_document)
        query_vectors, embedding_mode, fallback_reason = generate_embeddings_with_mode(
            [request.question],
            preferred_mode=preferred_mode,
            fallback_dimension=faiss_index.index.d if faiss_index.index is not None else None,
        )
        question_embedding = query_vectors[0]
        
        # Search for relevant chunks
        search_results = faiss_index.search(
            question_embedding,
            top_k=5,
            source=request.active_document
        )
        
        if not search_results:
            return ChatResponse(
                answer="I couldn't find relevant information in the uploaded documents.",
                sources=[],
                demo_mode=embedding_mode == FALLBACK_MODE,
                embedding_mode=embedding_mode
            )
        
        # Prepare context from top chunks
        context_parts = []
        sources = []
        for metadata, distance in search_results:
            context_parts.append(metadata["text"])
            sources.append({
                "text": metadata["text"][:200] + "..." if len(metadata["text"]) > 200 else metadata["text"],
                "source": metadata["source"],
                "chunk_id": metadata["chunk_id"],
                "relevance_score": 1.0 / (1.0 + distance)  # Convert distance to similarity score
            })
        
        context = "\n\n".join(context_parts)
        
        # Create prompt for LLM
        prompt = f"""Based on the following context from uploaded documents, answer the user's question. 
If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

Question: {request.question}

Answer:"""
        
        client = get_openai_client()
        if client is None:
            logger.warning("OpenAI chat client unavailable. Returning fallback demo answer.")
            return ChatResponse(
                answer=_build_demo_answer(request.question, search_results, fallback_reason),
                sources=sources,
                demo_mode=True,
                embedding_mode=embedding_mode,
            )

        # Get response from OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based only on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            answer = response.choices[0].message.content.strip()
        except Exception as error:
            logger.warning("OpenAI chat completion failed, returning fallback demo answer: %s", str(error))
            answer = _build_demo_answer(
                request.question,
                search_results,
                "OpenAI quota is unavailable, so the app is running in demo mode.",
            )
            return ChatResponse(
                answer=answer,
                sources=sources,
                demo_mode=True,
                embedding_mode=embedding_mode,
            )
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            demo_mode=embedding_mode == FALLBACK_MODE,
            embedding_mode=embedding_mode
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
