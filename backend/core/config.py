import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Toolboxx Chat Bot"
    debug: bool = True
    
    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # LLM Settings
    llm_provider: str = "openai"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # ChromaDB Settings
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "documents"
    
    # Document Settings
    documents_path: str = "./data/documents"
    chunk_size: int = 500
    chunk_overlap: int = 100
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"


settings = Settings()

