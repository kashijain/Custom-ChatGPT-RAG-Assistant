from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from ..utils.pdf_extractor import extract_text_from_pdf
from ..utils.text_chunker import chunk_text
from ..utils.embeddings import FALLBACK_MODE, generate_embeddings_with_mode
from ..utils.faiss_index import FAISSIndex

router = APIRouter()
UPLOAD_DIR = "uploads"
INDEX_DIR = "faiss_index"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

faiss_index = FAISSIndex(INDEX_DIR)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract text, chunk it, generate embeddings, and add to FAISS index.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    try:
        # Extract text
        text = extract_text_from_pdf(file_path)
        if not text:
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        # Chunk text
        chunks = chunk_text(text)
        
        # Generate embeddings with automatic fallback when OpenAI quota/API is unavailable.
        faiss_index.refresh()
        fallback_dimension = faiss_index.index.d if faiss_index.index is not None else None
        embeddings, embedding_mode, fallback_reason = generate_embeddings_with_mode(
            chunks,
            fallback_dimension=fallback_dimension
        )
        
        # Prepare metadata
        metadata = [
            {
                "text": chunk,
                "source": file.filename,
                "chunk_id": i,
                "embedding_mode": embedding_mode
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to FAISS index
        faiss_index.add_vectors(embeddings, metadata)
        
        message = "PDF uploaded and processed successfully"
        if embedding_mode == FALLBACK_MODE:
            message = "PDF uploaded and indexed in demo mode using fallback embeddings"

        return JSONResponse(
            content={
                "message": message,
                "filename": file.filename,
                "active_document": file.filename,
                "embedding_mode": embedding_mode,
                "demo_mode": embedding_mode == FALLBACK_MODE,
                "mode_notice": fallback_reason,
                "chunks_count": len(chunks),
                "total_text_length": len(text)
            },
            status_code=200
        )
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
