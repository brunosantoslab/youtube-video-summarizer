# api/presentation/routes/ai_optimization_routes.py
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from config import get_settings
from infrastructure.caching.redis_cache import RedisCache
from infrastructure.external.ai.ai_provider_client import AIProviderClient
from infrastructure.external.ai.budget_service import AIBudgetService
from infrastructure.caching.ai_cache_service import AICacheService

router = APIRouter(prefix="/api/ai-optimization", tags=["AI Optimization"])


# Models
class CacheStatsResponse(BaseModel):
    """Response model for cache statistics"""
    enabled: bool
    entries: int
    ttl: Optional[int] = None
    types: Dict[str, Any] = {}


class BudgetInfoResponse(BaseModel):
    """Response model for budget information"""
    date: str
    daily_budget: float
    current_cost: float
    remaining_budget: float
    percentage_used: float
    is_budget_exceeded: bool
    providers: Dict[str, Any] = {}


class UsageHistoryResponse(BaseModel):
    """Response model for usage history"""
    history: Dict[str, Any]
    total_cost: float
    days: int


class ClearCacheRequest(BaseModel):
    """Request model for clearing cache"""
    cache_type: Optional[str] = None


class ClearCacheResponse(BaseModel):
    """Response model for clearing cache"""
    cleared: int
    message: str


# Dependencies
def get_ai_provider_client():
    """Get AI provider client"""
    redis_cache = RedisCache()
    return AIProviderClient(redis_cache=redis_cache)


def get_budget_service():
    """Get budget service"""
    redis_cache = RedisCache()
    return AIBudgetService(redis_cache=redis_cache)


def get_cache_service():
    """Get cache service"""
    redis_cache = RedisCache()
    return AICacheService(redis_cache=redis_cache)


# Routes
@router.get("/cache-stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    ai_client: AIProviderClient = Depends(get_ai_provider_client)
):
    """Get AI cache statistics"""
    try:
        stats = await ai_client.get_cache_stats()
        return CacheStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cache stats: {str(e)}"
        )


@router.get("/budget-info", response_model=BudgetInfoResponse)
async def get_budget_info(
    budget_service: AIBudgetService = Depends(get_budget_service)
):
    """Get AI budget information"""
    try:
        budget_info = await budget_service.check_budget()
        return BudgetInfoResponse(**budget_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving budget info: {str(e)}"
        )


@router.get("/usage-history", response_model=UsageHistoryResponse)
async def get_usage_history(
    days: int = 7,
    budget_service: AIBudgetService = Depends(get_budget_service)
):
    """Get AI usage history"""
    try:
        history = await budget_service.get_usage_history(days)
        
        # Calculate total cost
        total_cost = 0.0
        for date, usage in history.items():
            total_cost += usage.get("total_cost", 0)
        
        return UsageHistoryResponse(
            history=history,
            total_cost=total_cost,
            days=days
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving usage history: {str(e)}"
        )


@router.post("/clear-cache", response_model=ClearCacheResponse)
async def clear_cache(
    request: ClearCacheRequest,
    cache_service: AICacheService = Depends(get_cache_service)
):
    """Clear AI cache"""
    try:
        cleared = await cache_service.clear_all(request.cache_type)
        cache_type_str = request.cache_type or "all"
        
        return ClearCacheResponse(
            cleared=cleared,
            message=f"Successfully cleared {cleared} entries from {cache_type_str} cache"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )
