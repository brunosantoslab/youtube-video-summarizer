# api/infrastructure/caching/redis_cache.py
import json
import logging
from typing import Optional, Any

# We'll handle the Redis import with try/except to avoid errors
try:
    import redis.asyncio as redis_async
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from config import get_settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis-based caching implementation"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or get_settings().redis_url
        self.redis_client = None
        
        if REDIS_AVAILABLE:
            self.redis_client = redis_async.from_url(self.redis_url)
        else:
            logger.warning("Redis package not installed. Caching will be disabled.")
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from the cache"""
        if not self.redis_client:
            return None
            
        try:
            value = await self.redis_client.get(key)
            if value:
                return value.decode("utf-8")
            return None
        except Exception as e:
            logger.error(f"Error retrieving key {key} from Redis: {str(e)}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a value in the cache with optional expiration in seconds"""
        if not self.redis_client:
            return False
            
        try:
            return await self.redis_client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {str(e)}")
            return False
    
    async def delete(self, key: str) -> int:
        """Delete a key from the cache"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {str(e)}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache"""
        if not self.redis_client:
            return False
            
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking if key {key} exists in Redis: {str(e)}")
            return False