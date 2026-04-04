from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Custom ChatGPT RAG API"
    api_v1_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    api_base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2

    chunk_size: int = 1200
    chunk_overlap: int = 200
    retrieval_top_k: int = 4
    max_upload_size_mb: int = 25

    backend_root: Path = Path(__file__).resolve().parents[2]
    upload_dir: Path = backend_root / "storage" / "uploads"
    faiss_index_path: Path = backend_root / "storage" / "faiss" / "index.faiss"
    faiss_metadata_path: Path = backend_root / "storage" / "faiss" / "metadata.pkl"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.faiss_index_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
