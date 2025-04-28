"""
Global pytest fixtures for unit tests
Author: Bruno Santos
"""
import sys
import os
from unittest.mock import MagicMock, AsyncMock
import pytest
from typing import Dict, Any

# Add the main API directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Mock fixtures for unit tests 

@pytest.fixture
def mock_database_session():
    """
    Create a mock database session.
    This fixture provides a mock SQLAlchemy session for unit tests.
    """
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.query = MagicMock(return_value=session)
    session.filter = MagicMock(return_value=session)
    session.filter_by = MagicMock(return_value=session)
    session.all = MagicMock(return_value=[])
    session.first = MagicMock(return_value=None)
    session.one = MagicMock(return_value=None)
    session.one_or_none = MagicMock(return_value=None)
    session.execute = MagicMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    session.flush = MagicMock()
    return session


@pytest.fixture
def mock_redis_client():
    """
    Create a mock Redis client.
    This fixture provides a mock Redis client for unit tests.
    """
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.exists = AsyncMock(return_value=0)
    redis.incr = AsyncMock(return_value=1)
    redis.incrby = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=1)
    redis.pipeline = AsyncMock()
    redis.hset = AsyncMock(return_value=1)
    redis.hget = AsyncMock(return_value=None)
    redis.hgetall = AsyncMock(return_value={})
    redis.hmset = AsyncMock(return_value=True)
    redis.hmget = AsyncMock(return_value=[])
    redis.hexists = AsyncMock(return_value=0)
    redis.hdel = AsyncMock(return_value=0)
    return redis


@pytest.fixture
def mock_settings(monkeypatch):
    """
    Create mock application settings and patch get_settings.
    This fixture provides mock settings for unit tests.
    
    Args:
        monkeypatch: pytest's monkeypatch fixture
    """
    from config import Settings
    
    # Create a mock settings object
    settings = Settings(
        # Required parameters
        database_url="sqlite:///:memory:",
        redis_url="redis://localhost:6379/0",
        youtube_api_key="test_api_key",
        youtube_client_id="test_client_id",
        youtube_client_secret="test_client_secret",
        youtube_redirect_uri="http://localhost:8000/callback",
        secret_key="test_secret_key",
        
        # Optional parameters with test values
        environment="test",
        debug=True,
        ai_cache_enabled=True,
        ai_cache_ttl=86400,
        ai_daily_budget=10.0,
    )
    
    # Patch the get_settings function to return our mock
    def mock_get_settings():
        return settings
    
    # Apply the patch
    import config
    monkeypatch.setattr(config, "get_settings", mock_get_settings)
    
    return settings


@pytest.fixture
def mock_event_publisher():
    """
    Create a mock event publisher.
    This fixture provides a mock event publisher for unit tests.
    """
    publisher = AsyncMock()
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def mock_repository_factory():
    """
    Create a mock repository factory.
    This fixture provides a mock repository factory for unit tests.
    """
    factory = MagicMock()
    # Setup to return a mock repository when called
    mock_repo = MagicMock()
    factory.get = MagicMock(return_value=mock_repo)
    return factory, mock_repo


# Override default pytest event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Override default event loop for pytest-asyncio."""
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
