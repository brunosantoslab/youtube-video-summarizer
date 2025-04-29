#!/usr/bin/env python
"""
Script to run integration tests without Docker.
This uses your Neon PostgreSQL database and a local mock Redis.
Author: Bruno Santos
"""
import os
import sys
import pytest
import asyncio
import tempfile
from unittest import mock

# Add mock classes for database and Redis
class MockRedis:
    """Mock Redis implementation for testing"""
    def __init__(self):
        self.data = {}
        self.expires = {}
    
    async def get(self, key):
        return self.data.get(key)
    
    async def set(self, key, value, ex=None):
        self.data[key] = value
        if ex:
            self.expires[key] = ex
        return True
    
    async def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                count += 1
        return count
    
    async def exists(self, *keys):
        return sum(1 for key in keys if key in self.data)
    
    async def hset(self, name, key, value):
        if name not in self.data:
            self.data[name] = {}
        self.data[name][key] = value
        return 1
    
    async def hget(self, name, key):
        if name in self.data and key in self.data[name]:
            return self.data[name][key]
        return None
    
    async def hgetall(self, name):
        return self.data.get(name, {})
    
    async def hmset(self, name, mapping):
        if name not in self.data:
            self.data[name] = {}
        self.data[name].update(mapping)
        return True
    
    async def hmget(self, name, keys):
        result = []
        for key in keys:
            if name in self.data and key in self.data[name]:
                result.append(self.data[name][key])
            else:
                result.append(None)
        return result
    
    async def hexists(self, name, key):
        return int(name in self.data and key in self.data[name])
    
    async def hdel(self, name, key):
        if name in self.data and key in self.data[name]:
            del self.data[name][key]
            return 1
        return 0
    
    async def incr(self, name):
        if name not in self.data:
            self.data[name] = "0"
        self.data[name] = str(int(self.data[name]) + 1)
        return int(self.data[name])
    
    async def incrby(self, name, amount):
        if name not in self.data:
            self.data[name] = "0"
        self.data[name] = str(int(self.data[name]) + amount)
        return int(self.data[name])
    
    async def expire(self, name, time):
        if name in self.data:
            self.expires[name] = time
            return 1
        return 0
    
    def pipeline(self):
        return MockRedisPipeline(self)
    
    async def init(self):
        """Mock initialization"""
        pass
    
    async def close(self):
        """Mock cleanup"""
        self.data.clear()
        self.expires.clear()


class MockRedisPipeline:
    """Mock Redis pipeline for testing"""
    def __init__(self, redis_instance):
        self.redis = redis_instance
        self.commands = []
    
    async def execute(self):
        results = []
        for cmd, args, kwargs in self.commands:
            method = getattr(self.redis, cmd)
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)
            results.append(result)
        return results
    
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            self.commands.append((name, args, kwargs))
            return self
        return wrapper
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.commands.clear()


def setup_test_environment():
    """Set up test environment for integration tests without Docker"""
    # Use Neon PostgreSQL database
    os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_PS0NT6DzdvRn@ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech/summary_tube_db?sslmode=require"
    
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    os.environ["TEMP_DIRECTORY"] = temp_dir
    
    # Create mock for Redis container
    redis_mock = MockRedis()
    
    # Create patches for TestContainers fixtures
    patches = [
        mock.patch('tests.integration.conftest.get_redis_container', return_value=redis_mock),
        # Add more patches as needed for other containers
    ]
    
    return patches, temp_dir


if __name__ == "__main__":
    # Set up test environment
    patches, temp_dir = setup_test_environment()
    
    # Apply all patches
    for p in patches:
        p.start()
    
    try:
        # Run the tests
        sys.exit(pytest.main(["-xvs", "tests/integration"]))
    finally:
        # Clean up patches
        for p in patches:
            p.stop()
        
        # Clean up temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass
