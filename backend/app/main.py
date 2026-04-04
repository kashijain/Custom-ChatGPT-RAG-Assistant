from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import logging
import os

# Configure basic application logging for startup/debug visibility.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from backend/.env before routes initialize.
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    masked_key = f"{openai_api_key[:7]}...{openai_api_key[-4:]}"
    logger.info("OPENAI_API_KEY loaded successfully from %s (%s).", ENV_PATH, masked_key)
else:
    logger.warning(
        "OPENAI_API_KEY is missing in %s. Embeddings will use deterministic fallback vectors, "
        "and chat responses will return a clear configuration error until the key is set."
        ,
        ENV_PATH,
    )

# Import routes only after loading environment variables so downstream modules
# can safely read os.getenv() during initialization.
from .routes import upload, chat

app = FastAPI(title="Custom ChatGPT RAG Assistant", version="1.0.0")

# CORS is required because the Vite frontend runs on a different origin/port
# than FastAPI during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Custom ChatGPT RAG Assistant API"}
