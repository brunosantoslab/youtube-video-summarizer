"""
Integration tests for Redis Cache using TestContainers
Author: Bruno Santos
"""
import json
import pytest
import asyncio

from infrastructure.caching.redis_cache import RedisCache


@pytest.mark.integration
class TestRedisCache:
    """Integration tests for Redis cache service"""
    
    @pytest.fixture
    async def redis_cache(self, redis_container):
        """Create a Redis cache instance connected to the test container"""
        redis_url = f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}"
        cache = RedisCache(redis_url)
        
        # Initialize and connect
        await cache.init()
        
        # Yield for the test
        yield cache
        
        # Clean up
        await cache.close()
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, redis_cache):
        """Test setting and getting a value from Redis"""
        # Set a value
        key = "test-key"
        value = {"name": "Test Value", "count": 42}
        
        success = await redis_cache.set(key, json.dumps(value))
        assert success is True
        
        # Get the value
        result = await redis_cache.get(key)
        assert result is not None
        
        # Verify the value
        parsed_result = json.loads(result)
        assert parsed_result == value
        assert parsed_result["name"] == "Test Value"
        assert parsed_result["count"] == 42
    
    @pytest.mark.asyncio
    async def test_get_missing_key(self, redis_cache):
        """Test getting a non-existent key"""
        result = await redis_cache.get("non-existent-key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_with_expiry(self, redis_cache):
        """Test setting a value with an expiry time"""
        # Set a value with a short expiry
        key = "expiring-key"
        value = "This will expire soon"
        
        success = await redis_cache.set(key, value, ex=1)  # 1 second expiry
        assert success is True
        
        # Verify the value can be retrieved immediately
        result = await redis_cache.get(key)
        assert result == value
        
        # Wait for it to expire
        await asyncio.sleep(1.5)
        
        # Verify the value is gone
        result = await redis_cache.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete(self, redis_cache):
        """Test deleting a value"""
        # Set a value
        key = "to-be-deleted"
        value = "This will be deleted"
        
        await redis_cache.set(key, value)
        
        # Verify it exists
        result = await redis_cache.get(key)
        assert result == value
        
        # Delete it
        deleted_count = await redis_cache.delete(key)
        assert deleted_count == 1
        
        # Verify it's gone
        result = await redis_cache.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_multi_delete(self, redis_cache):
        """Test deleting multiple values at once"""
        # Set multiple values
        keys = ["multi-1", "multi-2", "multi-3"]
        for i, key in enumerate(keys):
            await redis_cache.set(key, f"Value {i}")
        
        # Delete them all
        deleted_count = await redis_cache.delete(*keys)
        assert deleted_count == 3
        
        # Verify they're all gone
        for key in keys:
            result = await redis_cache.get(key)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_exists(self, redis_cache):
        """Test checking if keys exist"""
        # Set a value
        key = "existing-key"
        await redis_cache.set(key, "I exist")
        
        # Check if it exists
        exists = await redis_cache.exists(key)
        assert exists == 1
        
        # Check a non-existent key
        exists = await redis_cache.exists("non-existent-key")
        assert exists == 0
        
        # Check multiple keys
        await redis_cache.set("another-key", "I also exist")
        exists = await redis_cache.exists(key, "another-key", "non-existent-key")
        assert exists == 2  # Two out of three keys exist
    
    @pytest.mark.asyncio
    async def test_incr(self, redis_cache):
        """Test incrementing a counter"""
        # Set an initial value
        key = "counter"
        await redis_cache.set(key, "10")
        
        # Increment it
        new_value = await redis_cache.incr(key)
        assert new_value == 11
        
        # Increment it again
        new_value = await redis_cache.incr(key)
        assert new_value == 12
        
        # Increment by a specific amount
        new_value = await redis_cache.incrby(key, 5)
        assert new_value == 17
    
    @pytest.mark.asyncio
    async def test_expire(self, redis_cache):
        """Test setting expiry on existing keys"""
        # Set a value without expiry
        key = "will-expire"
        await redis_cache.set(key, "Set to expire")
        
        # Set expiry
        success = await redis_cache.expire(key, 1)  # 1 second
        assert success == 1
        
        # Verify it exists before expiry
        exists = await redis_cache.exists(key)
        assert exists == 1
        
        # Wait for it to expire
        await asyncio.sleep(1.5)
        
        # Verify it's gone
        exists = await redis_cache.exists(key)
        assert exists == 0
    
    @pytest.mark.asyncio
    async def test_pipeline(self, redis_cache):
        """Test Redis pipeline (multiple operations at once)"""
        # Use a pipeline
        async with redis_cache.pipeline() as pipe:
            pipe.set("pipe-key-1", "value-1")
            pipe.set("pipe-key-2", "value-2")
            pipe.get("pipe-key-1")
            pipe.get("pipe-key-2")
            results = await pipe.execute()
        
        # Verify results
        assert results[0] is True  # First set was successful
        assert results[1] is True  # Second set was successful
        assert results[2] == "value-1"  # Get result
        assert results[3] == "value-2"  # Get result
        
        # Verify keys exist in Redis
        exists = await redis_cache.exists("pipe-key-1", "pipe-key-2")
        assert exists == 2
    
    @pytest.mark.asyncio
    async def test_hash_operations(self, redis_cache):
        """Test Redis hash operations"""
        hash_key = "test-hash"
        
        # Set hash fields
        await redis_cache.hset(hash_key, "field1", "value1")
        await redis_cache.hset(hash_key, "field2", "value2")
        
        # Get single field
        value1 = await redis_cache.hget(hash_key, "field1")
        assert value1 == "value1"
        
        # Get all fields
        all_fields = await redis_cache.hgetall(hash_key)
        assert all_fields == {"field1": "value1", "field2": "value2"}
        
        # Check if field exists
        exists = await redis_cache.hexists(hash_key, "field1")
        assert exists == 1
        
        exists = await redis_cache.hexists(hash_key, "nonexistent")
        assert exists == 0
        
        # Delete a field
        deleted = await redis_cache.hdel(hash_key, "field1")
        assert deleted == 1
        
        # Verify field is gone
        exists = await redis_cache.hexists(hash_key, "field1")
        assert exists == 0
        
        # Set multiple fields at once
        await redis_cache.hmset(hash_key, {"field3": "value3", "field4": "value4"})
        
        # Get multiple fields
        values = await redis_cache.hmget(hash_key, "field2", "field3", "field4")
        assert values == ["value2", "value3", "value4"]
