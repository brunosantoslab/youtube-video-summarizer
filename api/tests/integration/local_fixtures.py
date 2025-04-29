"""
Local fixtures for integration tests without Docker
Author: Bruno Santos
"""
import pytest
import asyncio
from unittest import mock

# Fixtures for database sessions
@pytest.fixture
async def db_session():
    """Provide a database session for tests using Neon PostgreSQL"""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    import os
    
    # Get database URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Create an async database URL if needed
    if not database_url.startswith("postgresql+asyncpg"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Create engine and session
    engine = create_async_engine(database_url)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Create a session
    async with async_session() as session:
        # Begin a transaction
        async with session.begin():
            # Return the session for tests
            yield session
            
            # Roll back the transaction after the test
            await session.rollback()

# Fixture for test client
@pytest.fixture
async def client():
    """Provide a test client for API tests"""
    from fastapi.testclient import TestClient
    from main import app
    
    # Create a test client
    with TestClient(app) as test_client:
        yield test_client

# Fixture for mock settings
@pytest.fixture
def mock_settings():
    """Provide mock settings for tests"""
    from config import Settings
    
    # Create mock settings
    settings = Settings(
        # Database
        database_url="postgresql://neondb_owner:password@localhost:5432/test_db",
        
        # Redis
        redis_url="redis://localhost:6379/0",
        
        # YouTube API
        youtube_api_key="mock_api_key",
        youtube_client_id="mock_client_id",
        youtube_client_secret="mock_client_secret",
        youtube_redirect_uri="http://localhost:8000/auth/youtube/callback",
        
        # Application
        secret_key="mock_secret_key",
        debug=True,
        environment="test",
    )
    
    # Return the mock settings
    return settings

# Fixtures to replace TestContainers
@pytest.fixture
async def redis_container():
    """Mock Redis container for tests"""
    # Create a mock Redis
    class MockRedis:
        async def get(self, key):
            return None
            
        async def set(self, key, value, ex=None):
            return True
            
        def get_container_host_ip(self):
            return "localhost"
            
        def get_exposed_port(self, port):
            return 6379
    
    # Return the mock Redis
    return MockRedis()
