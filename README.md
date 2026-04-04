# 🚀 Custom ChatGPT (RAG-based AI Assistant)

> 💡 A modern AI-powered assistant to chat with your PDFs using RAG (Retrieval-Augmented Generation)

---

## 🧠 Overview

This is a **full-stack AI application** where users can upload PDF documents and ask questions based on their content.

It combines:
- 🤖 LLMs (AI)
- 🔍 Vector Search (FAISS)
- 🌐 Full Stack Development

---

## ✨ Features

- 📄 Upload and analyze PDF documents  
- 💬 ChatGPT-like conversational UI  
- 🔍 Semantic search using embeddings + FAISS  
- 🧠 Context-aware answers from documents  
- ⚡ Fast retrieval using vector similarity  
- 🧪 Demo mode (works without OpenAI quota)  
- 🎨 Premium UI (React + Tailwind + Framer Motion)

---

## 🏗️ Tech Stack

### 🎨 Frontend
- React (Vite)
- Tailwind CSS
- Framer Motion
- Axios

### ⚙️ Backend
- FastAPI (Python)
- FAISS (Vector Database)
- OpenAI API (Embeddings + LLM)
- Python (RAG Pipeline)

---

## ⚙️ How It Works

1. 📄 Upload PDF  
2. ✂️ Split into chunks  
3. 🔢 Convert to embeddings  
4. 📦 Store in FAISS  
5. ❓ Ask question  
6. 🔍 Retrieve relevant chunks  
7. 🤖 Generate answer  

---

## 📁 Project Structure
custom-chatgpt-rag/
├── backend/
├── frontend/
├── README.md


---

## 🔑 Environment Setup

Create a `.env` file inside `backend/`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
FALLBACK_EMBEDDING_DIM=1536

---

🚀 Run Locally
Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
Frontend
cd frontend
npm install
npm run dev

---

🌐 API Endpoints
Method	Endpoint	Description
POST	/api/upload	Upload PDF
POST	/api/chat	Ask questions

---

📸 Screenshots
<img width="1853" height="950" alt="image" src="https://github.com/user-attachments/assets/c788b4da-250f-4a2e-bca6-e703b1702cd6" />

---

🚀 Future Improvements
Multi-PDF support
Chat history
Authentication
Source highlighting
Deployment

---

👨‍💻 Author

Kashish Jain
🔗 GitHub: https://github.com/kashijain

🔗 LinkedIn: https://www.linkedin.com/in/kashishjain-tech/

