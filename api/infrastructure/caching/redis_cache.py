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
    
    async def delete(self, *keys) -> int:
        """Delete a key from the cache"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting keys from Redis: {str(e)}")
            return 0
    
    async def exists(self, *keys) -> int:
        """Check if key(s) exist in the cache
        Returns: The number of keys that exist
        """
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.exists(*keys)
        except Exception as e:
            logger.error(f"Error checking if keys exist in Redis: {str(e)}")
            return 0
    
    async def hset(self, name: str, key: str, value: str) -> int:
        """Set a hash field to the specified value"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.hset(name, key, value)
        except Exception as e:
            logger.error(f"Error setting hash {name} field {key} in Redis: {str(e)}")
            return 0
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get the value of a hash field"""
        if not self.redis_client:
            return None
            
        try:
            value = await self.redis_client.hget(name, key)
            if value:
                return value.decode("utf-8")
            return None
        except Exception as e:
            logger.error(f"Error getting hash {name} field {key} from Redis: {str(e)}")
            return None
    
    async def hgetall(self, name: str) -> dict:
        """Get all the fields and values in a hash"""
        if not self.redis_client:
            return {}
            
        try:
            result = await self.redis_client.hgetall(name)
            return {k.decode("utf-8"): v.decode("utf-8") for k, v in result.items()}
        except Exception as e:
            logger.error(f"Error getting all fields from hash {name} in Redis: {str(e)}")
            return {}
    
    async def hmset(self, name: str, mapping: dict) -> bool:
        """Set multiple hash fields to multiple values"""
        if not self.redis_client:
            return False
            
        try:
            return await self.redis_client.hset(name, mapping=mapping)
        except Exception as e:
            logger.error(f"Error setting multiple fields in hash {name} in Redis: {str(e)}")
            return False
    
    async def hmget(self, name: str, keys: list) -> list:
        """Get the values of all the given hash fields"""
        if not self.redis_client:
            return [None] * len(keys)
            
        try:
            result = await self.redis_client.hmget(name, keys)
            return [v.decode("utf-8") if v else None for v in result]
        except Exception as e:
            logger.error(f"Error getting multiple fields from hash {name} in Redis: {str(e)}")
            return [None] * len(keys)
    
    async def hexists(self, name: str, key: str) -> int:
        """Check if a hash field exists"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.hexists(name, key)
        except Exception as e:
            logger.error(f"Error checking if field {key} exists in hash {name} in Redis: {str(e)}")
            return 0
    
    async def hdel(self, name: str, key: str) -> int:
        """Delete a hash field"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.hdel(name, key)
        except Exception as e:
            logger.error(f"Error deleting field {key} from hash {name} in Redis: {str(e)}")
            return 0
    
    async def incr(self, name: str) -> int:
        """Increment the integer value of a key by one"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.incr(name)
        except Exception as e:
            logger.error(f"Error incrementing key {name} in Redis: {str(e)}")
            return 0
    
    async def incrby(self, name: str, amount: int) -> int:
        """Increment the integer value of a key by the given amount"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.incrby(name, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {name} by {amount} in Redis: {str(e)}")
            return 0
    
    async def expire(self, name: str, time: int) -> int:
        """Set a key's time to live in seconds"""
        if not self.redis_client:
            return 0
            
        try:
            return await self.redis_client.expire(name, time)
        except Exception as e:
            logger.error(f"Error setting expiry for key {name} in Redis: {str(e)}")
            return 0
    
    def pipeline(self):
        """Return a pipeline object that can execute multiple commands in a batch"""
        if not self.redis_client:
            logger.error("Cannot create pipeline - Redis client not available")
            return None
            
        return self.redis_client.pipeline()
    
    async def init(self):
        """Initialize the Redis connection"""
        # Connection is already established in __init__, this is just a placeholder
        # for compatibility with test fixtures
        pass
    
    async def close(self):
        """Close the Redis connection"""
        if self.redis_client:
            await self.redis_client.close()