# api/infrastructure/external/ai/budget_service.py
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union

from infrastructure.caching.redis_cache import RedisCache
from config import get_settings

logger = logging.getLogger(__name__)


class AIBudgetService:
    """Service for tracking and managing AI usage costs"""
    
    def __init__(self, redis_cache: RedisCache = None):
        self.settings = get_settings()
        self.redis_cache = redis_cache or RedisCache()
        self.costs = self.settings.ai_provider_costs
        # Ensure daily_budget is a float
        self.daily_budget = float(self.settings.ai_daily_budget)
    
    async def track_usage(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """
        Track usage costs for AI operations
        
        Args:
            provider: AI provider name (openai, google)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        # Calculate cost
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens)
        
        # Update usage statistics in Redis
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get current usage
        key = f"ai:usage:{today}"
        usage = await self._get_usage(key)
        
        # Update usage data
        usage["total_cost"] = usage.get("total_cost", 0) + cost
        usage["providers"] = usage.get("providers", {})
        
        if provider not in usage["providers"]:
            usage["providers"][provider] = {}
            
        if model not in usage["providers"][provider]:
            usage["providers"][provider][model] = {
                "cost": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "requests": 0
            }
        
        # Update model usage
        model_usage = usage["providers"][provider][model]
        model_usage["cost"] += cost
        model_usage["input_tokens"] += input_tokens
        model_usage["output_tokens"] += output_tokens
        model_usage["requests"] += 1
        
        # Save updated usage
        await self._set_usage(key, usage)
        
        # Log usage
        logger.info(
            f"AI Usage: {provider}/{model} - {input_tokens} in, {output_tokens} out. "
            f"Cost: ${cost:.4f}, Daily total: ${usage['total_cost']:.4f}"
        )
        
        return cost
    
    async def check_budget(self) -> Dict[str, Any]:
        """
        Check current budget status
        
        Returns:
            Dictionary with budget information
        """
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"ai:usage:{today}"
        usage = await self._get_usage(key)
        
        current_cost = float(usage.get("total_cost", 0))
        daily_budget = float(self.daily_budget)  # Ensure it's a float
        
        remaining_budget = daily_budget - current_cost
        
        # Safe division to avoid errors
        if daily_budget > 0:
            percentage_used = (current_cost / daily_budget) * 100
        else:
            percentage_used = 0
        
        return {
            "date": today,
            "daily_budget": daily_budget,
            "current_cost": current_cost,
            "remaining_budget": remaining_budget,
            "percentage_used": percentage_used,
            "is_budget_exceeded": current_cost >= daily_budget,
            "providers": usage.get("providers", {})
        }
    
    async def is_within_budget(self) -> bool:
        """
        Check if current usage is within budget
        
        Returns:
            True if within budget, False otherwise
        """
        budget_info = await self.check_budget()
        return not budget_info["is_budget_exceeded"]
    
    async def get_usage_history(self, days: int = 7) -> Dict[str, Any]:
        """
        Get usage history for the specified number of days
        
        Args:
            days: Number of days of history to retrieve
            
        Returns:
            Dictionary with usage history
        """
        history = {}
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            key = f"ai:usage:{date}"
            usage = await self._get_usage(key)
            
            if usage and usage.get("total_cost", 0) > 0:
                history[date] = usage
        
        return history
    
    async def _get_usage(self, key: str) -> Dict[str, Any]:
        """Get usage data from Redis"""
        result = await self.redis_cache.get(key)
        if result:
            return json.loads(result)
        return {}
    
    async def _set_usage(self, key: str, usage: Dict[str, Any]) -> bool:
        """Set usage data in Redis"""
        return await self.redis_cache.set(key, json.dumps(usage), ex=86400 * 7)  # Keep for 7 days
    
    def _calculate_cost(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Calculate cost for the given usage"""
        if provider not in self.costs:
            logger.warning(f"No cost information for provider: {provider}")
            return 0
            
        if model not in self.costs[provider]:
            logger.warning(f"No cost information for model: {model}")
            return 0
        
        model_costs = self.costs[provider][model]
        input_cost = (input_tokens / 1000) * float(model_costs["input"])
        output_cost = (output_tokens / 1000) * float(model_costs["output"])
        
        return input_cost + output_cost
    
    def estimate_cost(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        estimated_output_tokens: int
    ) -> float:
        """
        Estimate cost before performing an operation
        
        Args:
            provider: AI provider name
            model: Model name
            input_tokens: Number of input tokens
            estimated_output_tokens: Estimated number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        return self._calculate_cost(provider, model, input_tokens, estimated_output_tokens)