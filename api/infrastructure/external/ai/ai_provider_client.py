# api/infrastructure/external/ai/ai_provider_client.py
import logging
from typing import Dict, List, Any, Optional

from config import get_settings
from infrastructure.external.ai.provider_interface import AIProviderInterface
from infrastructure.external.ai.openai_client import OpenAIClient
from infrastructure.external.ai.google_client import GoogleAIClient
from infrastructure.caching.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class AIProviderClient:
    """Client that manages multiple AI providers"""
    
    def __init__(
        self, 
        config=None, 
        redis_cache: Optional[RedisCache] = None
    ):
        self.config = config or get_settings()
        self.redis_cache = redis_cache
        
        # Initialize providers
        self.openai_client = OpenAIClient(self.config.openai_api_key)
        self.google_client = GoogleAIClient(self.config.google_ai_api_key)
        
        # Map provider names to client instances
        self.providers = {
            "openai": self.openai_client,
            "google": self.google_client
        }
        
        # Default provider
        self.default_provider = self.config.default_ai_provider or "openai"
    
    async def generate_summary(
        self, 
        transcript_text: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary from transcript text
        
        Args:
            transcript_text: Text to summarize
            model: Specific model to use
            max_tokens: Maximum tokens for summary
            provider: AI provider to use (openai, google)
            
        Returns:
            Dictionary with summary result
        """
        # Set defaults
        provider = provider or self.default_provider
        max_tokens = max_tokens or 500
        
        # Check cache if available
        if self.redis_cache:
            cache_key = f"summary:{provider}:{hash(transcript_text)}:{max_tokens}"
            cached_result = await self.redis_cache.get(cache_key)
            if cached_result:
                import json
                return json.loads(cached_result)
        
        try:
            # Get provider client
            if provider not in self.providers:
                raise ValueError(f"Unsupported AI provider: {provider}")
            
            client = self.providers[provider]
            
            # Generate summary
            result = await client.generate_summary(
                transcript_text=transcript_text,
                max_length=max_tokens,
                model=model
            )
            
            # Cache result if possible
            if self.redis_cache:
                import json
                await self.redis_cache.set(
                    cache_key, 
                    json.dumps(result), 
                    ex=86400  # Cache for 24 hours
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error with {provider}: {str(e)}, trying fallback")
            
            # Try fallback provider if configured and different
            fallback_provider = self.config.fallback_ai_provider
            if fallback_provider and fallback_provider != provider:
                try:
                    client = self.providers[fallback_provider]
                    return await client.generate_summary(
                        transcript_text=transcript_text,
                        max_length=max_tokens,
                        model=model
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback provider {fallback_provider} also failed: {str(fallback_error)}")
            
            # Re-raise the original error if no fallback or fallback failed
            raise