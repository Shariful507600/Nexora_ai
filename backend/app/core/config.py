# ============================================
# NEXORA AI - Core Configuration
# ============================================
# এই ফাইলটি .env থেকে সব settings লোড করে
# এবং সারা অ্যাপে ব্যবহারের জন্য একটি
# central config object তৈরি করে।

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    lru_cache ব্যবহার করে একবারই লোড হয় - performance optimization.
    """

    # App Info
    APP_NAME: str = "NEXORA AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "nexora-secret-key"

    # PostgreSQL Database URL
    DATABASE_URL: str = "postgresql+asyncpg://nexora_user:nexora_pass@localhost:5432/nexora_db"

    # ChromaDB Vector Store
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION: str = "nexora_docs"

    # Ollama Local LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "tinyllama"
    OLLAMA_TIMEOUT: int = 120

    # Cloud AI Fallback (Optional)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    USE_CLOUD_FALLBACK: bool = False

    # JWT Authentication
    JWT_SECRET_KEY: str = "nexora-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # File Upload Settings
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"

    # CORS - Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Settings এর একটিমাত্র instance তৈরি করে।
    Dependency injection এর মাধ্যমে পুরো app এ ব্যবহার হয়।
    """
    return Settings()


# Global settings object - সব জায়গায় import করে ব্যবহার করা যাবে
settings = get_settings()
