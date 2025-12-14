"""
Application settings and configuration.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://inventory_user:inventory_password@localhost:5432/inventory_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Authentication
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API
    api_v1_prefix: str = "/v1"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Logging
    log_level: str = "INFO"
    
    # AI Service
    ai_service_url: Optional[str] = "http://localhost:8001"
    
    # Voice Service
    voice_service_url: Optional[str] = "http://localhost:8002"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

