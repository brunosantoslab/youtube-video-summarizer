# api/config.py
from functools import lru_cache
from typing import Optional, Dict

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
    default_ai_provider: str = "openai"
    fallback_ai_provider: str = "google"
    
    # AI Cost Optimization
    ai_cache_enabled: bool = True
    ai_cache_ttl: int = 86400  # 24 hours in seconds
    ai_daily_budget: float = 10.0  # Daily budget in USD
    ai_token_optimization_enabled: bool = True
    ai_prompt_optimization_enabled: bool = True
    
    # AI Provider costs per 1K tokens (input/output) in USD
    ai_provider_costs: Dict[str, Dict[str, float]] = {
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        },
        "google": {
            "gemini-pro": {"input": 0.00125, "output": 0.00375}
        }
    }
    
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