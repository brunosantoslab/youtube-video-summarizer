# api/infrastructure/external/ai/ai_provider_client.py
import logging
from typing import Dict, Any, Optional

from config import get_settings
from infrastructure.external.ai.provider_interface import AIProviderInterface
from infrastructure.external.ai.openai_client import OpenAIClient
from infrastructure.external.ai.google_client import GoogleAIClient
from infrastructure.caching.redis_cache import RedisCache
from infrastructure.caching.ai_cache_service import AICacheService
from infrastructure.external.ai.budget_service import AIBudgetService
from infrastructure.external.ai.token_optimizer import TokenOptimizer

logger = logging.getLogger(__name__)


class AIProviderClient:
    """Client that manages multiple AI providers with caching and cost optimization"""
    
    def __init__(
        self, 
        config=None, 
        redis_cache: Optional[RedisCache] = None
    ):
        self.config = config or get_settings()
        self.redis_cache = redis_cache or RedisCache()
        
        # Initialize optimization services
        self.cache_service = AICacheService(self.redis_cache)
        self.budget_service = AIBudgetService(self.redis_cache)
        self.token_optimizer = TokenOptimizer()
        
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
        self.fallback_provider = self.config.fallback_ai_provider or "google"
        
        # Optimization flags
        self.token_optimization_enabled = self.config.ai_token_optimization_enabled
        self.prompt_optimization_enabled = self.config.ai_prompt_optimization_enabled
    
    async def generate_summary(
        self, 
        transcript_text: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary from transcript text with caching and cost optimization
        
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
        model = model or "gpt-4" if provider == "openai" else "gemini-pro"
        max_tokens = max_tokens or 500
        
        # Check budget first
        budget_ok = await self.budget_service.is_within_budget()
        if not budget_ok:
            logger.warning("AI budget exceeded, using cached results only")
            # Will still try to get from cache, but won't make new API calls
        
        # Generate a hash for the transcript to use in caching
        transcript_hash = self.cache_service.get_content_hash(transcript_text)
        
        # Try to get from cache first
        cached_result = await self.cache_service.get_summary(
            transcript_hash=transcript_hash,
            provider=provider,
            model=model,
            max_tokens=max_tokens
        )
        
        if cached_result:
            logger.info(f"Using cached summary for {provider}/{model}")
            return cached_result
        
        # If budget exceeded and no cache, return error
        if not budget_ok:
            raise ValueError("Daily AI budget exceeded and no cached result available")
        
        # Apply token optimization if enabled
        if self.token_optimization_enabled:
            # Get default max input tokens based on provider/model
            max_input_tokens = 6000 if provider == "openai" else 8000
            
            # Optimize the transcript
            optimized_transcript, token_count = self.token_optimizer.optimize_transcript(
                transcript=transcript_text,
                max_tokens=max_input_tokens,
                model=model
            )
            
            # Use the optimized transcript
            transcript_to_use = optimized_transcript
        else:
            # Use original transcript
            transcript_to_use = transcript_text
            token_count = self.token_optimizer.count_tokens(transcript_text, model)
        
        # Estimate the cost before making the API call
        estimated_cost = self.budget_service.estimate_cost(
            provider=provider,
            model=model,
            input_tokens=token_count,
            estimated_output_tokens=max_tokens
        )
        
        logger.info(
            f"Estimated cost for {provider}/{model}: ${estimated_cost:.4f} "
            f"({token_count} input tokens, ~{max_tokens} output tokens)"
        )
        
        try:
            # Get provider client
            if provider not in self.providers:
                raise ValueError(f"Unsupported AI provider: {provider}")
            
            client = self.providers[provider]
            
            # Generate summary
            result = await client.generate_summary(
                transcript_text=transcript_to_use,
                max_length=max_tokens,
                model=model
            )
            
            # Track usage for budget
            await self.budget_service.track_usage(
                provider=provider,
                model=model,
                input_tokens=token_count,
                output_tokens=result["metadata"].get("token_count", max_tokens)
            )
            
            # Cache the result
            await self.cache_service.set_summary(
                transcript_hash=transcript_hash,
                provider=provider,
                model=model,
                max_tokens=max_tokens,
                summary_data=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error with {provider}: {str(e)}")
            
            # Try fallback provider if configured and different
            if self.fallback_provider and self.fallback_provider != provider:
                logger.info(f"Trying fallback provider: {self.fallback_provider}")
                
                try:
                    return await self.generate_summary(
                        transcript_text=transcript_text,
                        model=None,  # Use default for fallback provider
                        max_tokens=max_tokens,
                        provider=self.fallback_provider
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback provider {self.fallback_provider} also failed: {str(fallback_error)}")
            
            # Re-raise the original error if no fallback or fallback failed
            raise
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the AI cache"""
        return await self.cache_service.get_cache_stats()
    
    async def get_budget_info(self) -> Dict[str, Any]:
        """Get information about the current AI budget usage"""
        return await self.budget_service.check_budget()
    
    async def get_usage_history(self, days: int = 7) -> Dict[str, Any]:
        """Get AI usage history for the specified number of days"""
        return await self.budget_service.get_usage_history(days)
    
    async def clear_cache(self, cache_type: Optional[str] = None) -> int:
        """Clear the AI cache"""
        return await self.cache_service.clear_all(cache_type)