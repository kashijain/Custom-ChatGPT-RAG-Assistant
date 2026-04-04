from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.models.schemas import SourceSnippet
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.vector_store import FAISSVectorStore
from app.utils.pdf_loader import extract_text_from_pdf
from app.utils.text_splitter import chunk_text


class RAGService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        vector_store: FAISSVectorStore,
        chunk_size: int,
        chunk_overlap: int,
        retrieval_top_k: int,
        upload_dir: Path,
    ) -> None:
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retrieval_top_k = retrieval_top_k
        self.upload_dir = upload_dir

    async def ingest_pdf(self, file: UploadFile, max_upload_size_bytes: int) -> tuple[str, str, int]:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please upload a valid PDF file.",
            )

        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )
        if len(file_bytes) > max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Uploaded file exceeds the configured size limit.",
            )

        document_id = str(uuid4())
        safe_filename = Path(file.filename).name
        destination = self.upload_dir / f"{document_id}_{safe_filename}"
        destination.write_bytes(file_bytes)

        try:
            document_text = extract_text_from_pdf(destination)
        except Exception as exc:
            if destination.exists():
                destination.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from PDF: {str(exc)}",
            ) from exc

        chunks = chunk_text(
            document_text,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        if not chunks:
            if destination.exists():
                destination.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No extractable text was found in the uploaded PDF.",
            )

        try:
            embeddings = await self.embedding_service.embed_texts(chunks)
            metadata = [
                {
                    "document_id": document_id,
                    "filename": safe_filename,
                    "chunk_index": index,
                    "text": chunk,
                }
                for index, chunk in enumerate(chunks)
            ]
            chunks_indexed = self.vector_store.add_chunks(embeddings, metadata)
        except Exception:
            if destination.exists():
                destination.unlink()
            raise

        return document_id, safe_filename, chunks_indexed

    async def answer_question(
        self,
        question: str,
        document_id: str | None = None,
        top_k: int | None = None,
    ) -> tuple[str, list[SourceSnippet]]:
        query_embedding = (await self.embedding_service.embed_texts([question]))[0]
        retrieved_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k or self.retrieval_top_k,
            document_id=document_id,
        )

        if not retrieved_chunks:
            return (
                "I couldn't find relevant content in the uploaded documents for that question.",
                [],
            )

        context = "\n\n".join(
            f"[Source {idx + 1} | {chunk['filename']} | Chunk {chunk['chunk_index']}]\n{chunk['text']}"
            for idx, chunk in enumerate(retrieved_chunks)
        )
        answer = await self.llm_service.generate_answer(question=question, context=context)

        sources = [
            SourceSnippet(
                document_id=chunk["document_id"],
                filename=chunk["filename"],
                chunk_index=chunk["chunk_index"],
                score=chunk["score"],
                text=chunk["text"],
            )
            for chunk in retrieved_chunks
        ]

        return answer, sources
