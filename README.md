🚀 Custom ChatGPT (RAG-based AI Assistant)
🧠 Overview

A full-stack AI-powered assistant that allows users to upload PDFs and ask questions based on their content using Retrieval-Augmented Generation (RAG).

This project combines LLMs + Vector Search + Full Stack Development to build a real-world AI product.

✨ Features
📄 Upload and process PDF documents
🔍 Semantic search using embeddings + FAISS
💬 ChatGPT-like conversational interface
📚 Context-aware answers from uploaded documents
🧠 RAG pipeline (Retrieval + Generation)
⚡ Fast document retrieval using vector similarity
🧪 Demo mode (works without OpenAI quota)
🎨 Modern aesthetic UI (React + Tailwind)
🏗️ Tech Stack
Frontend
React (Vite)
Tailwind CSS
Framer Motion
Axios
Backend
FastAPI (Python)
FAISS (Vector Database)
OpenAI API (Embeddings + LLM)
Python (RAG pipeline)
⚙️ How It Works
User uploads a PDF
Text is extracted and split into chunks
Each chunk is converted into embeddings
Embeddings are stored in FAISS
User asks a question
Relevant chunks are retrieved
LLM generates answer using retrieved context
📁 Project Structure
custom-chatgpt-rag/
├── backend/
│   ├── app/
│   ├── uploads/
│   ├── faiss_index/
│   ├── main.py
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── components/
│   └── App.jsx
│
└── README.md
🔑 Environment Setup

Create a .env file inside backend/:

OPENAI_API_KEY=your_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
FALLBACK_EMBEDDING_DIM=1536
🚀 Run Locally
Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
Frontend
cd frontend
npm install
npm run dev
🌐 API Endpoints
POST /api/upload → Upload PDF
POST /api/chat → Ask questions
⚠️ Notes
If OpenAI quota is not available, app runs in demo mode
.env file is not included for security reasons
💼 Use Cases
📚 Study assistant for notes & books
📄 Resume / document analysis
🧠 Knowledge base chatbot
🏢 Internal company document assistant
📸 Screenshots
<img width="1852" height="947" alt="image" src="https://github.com/user-attachments/assets/36f5e95e-b9dc-48f0-b262-be8c4c86dbc9" />
🚀 Future Improvements
Multi-PDF support
Chat history
Authentication system
Source highlighting
Deployment (Vercel + Render)
👨‍💻 Author

Kashish Jain

GitHub: https://github.com/kashijain
LinkedIn: https://www.linkedin.com/in/kashishjain-tech/
⭐ If you like this project

Give it a ⭐ on GitHub and support the project!
