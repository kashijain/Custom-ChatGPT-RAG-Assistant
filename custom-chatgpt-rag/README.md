# Custom ChatGPT (RAG-based AI Assistant)

MVP full-stack RAG assistant where users upload PDFs and ask questions grounded in the uploaded document content.

## Project Structure

```text
custom-chatgpt-rag/
  backend/
    app/
    storage/
    .env.example
    requirements.txt
  frontend/
```

## Backend Setup

```bash
cd custom-chatgpt-rag/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `API_KEY` plus your API-compatible model settings.

## Run Backend

```bash
uvicorn app.main:app --reload
```

Backend health check: `GET http://localhost:8000/health`

## API Endpoints

- `POST /api/upload` with multipart form field `file` containing a PDF
- `POST /api/chat` with JSON body:

```json
{
  "question": "What is this document about?",
  "document_id": "optional-uploaded-document-id",
  "top_k": 4
}
```

## Notes

- PDF files are stored locally in `backend/storage/uploads`.
- FAISS index and chunk metadata are stored locally in `backend/storage/faiss`.
- Answers are generated from retrieved document chunks only; if no relevant chunk is found, the API returns a fallback message.
