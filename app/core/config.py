from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Financial Document Management API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/financial_rag"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production-at-least-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "financial_documents"

    # Embeddings
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    USE_LOCAL_EMBEDDINGS: bool = True

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
