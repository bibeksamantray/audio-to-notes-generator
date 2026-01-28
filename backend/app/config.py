import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or defaults."""

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "lecture_notes_db"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR.parent.parent / "data"
    AUDIO_DIR: Path = DATA_DIR / "audio"
    EXPORTS_DIR: Path = DATA_DIR / "exports"

    # Whisper model
    WHISPER_MODEL_SIZE: str = "small"  # "tiny", "base", "small", "medium", etc.

    # LLM (Ollama / LM Studio)
    LLM_BACKEND: str = "ollama"  # currently only Ollama implemented
    LLM_MODEL_NAME: str = "mistral:7b"  # Using Mistral 7B (~4GB) - better reasoning and note generation. Alternatives: "phi3" (~2.3GB), "llama3.2" (~2GB), "tinyllama" (~637MB - faster but lower quality)
    LLM_API_BASE_URL: str = "http://localhost:11434"  # Ollama default

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure required directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)