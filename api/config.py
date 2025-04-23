# api/config.py
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # YouTube API
    youtube_api_key: str
    youtube_client_id: str
    youtube_client_secret: str
    youtube_redirect_uri: str
    
    # AI Providers
    openai_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    
    # Application
    secret_key: str
    debug: bool = False
    environment: str = "development"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings"""
    return Settings()