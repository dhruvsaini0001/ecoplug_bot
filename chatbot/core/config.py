"""
Configuration Management
Centralized environment configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "EV Charging Diagnostic Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_PREFIX: str = "/v1"
    CORS_ORIGINS: list[str] = ["*"]
    
    # # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ev_chatbot_db"
    MONGODB_MAX_CONNECTIONS: int = 10
    MONGODB_MIN_CONNECTIONS: int = 1
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    
    # AI Service Configuration (Future OpenAI Integration Point)
    # When ready to integrate OpenAI:
    # 1. Set OPENAI_API_KEY in .env file
    # 2. Uncomment ai_service.py OpenAI client initialization
    # 3. Replace mock response with actual API call
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 500
    
    # Rate Limiting (Placeholder for future middleware)
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Knowledge Base Paths
    ERROR_CODES_PATH: str = "error_codes_complete.json"
    FLOWS_PATH: str = "chatbot/flows/chatbot_flows.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Create cached settings instance.
    This ensures settings are loaded only once during application lifecycle.
    """
    return Settings()
