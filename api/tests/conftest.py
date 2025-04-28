"""
Global pytest fixtures for integration tests using TestContainers
Author: Bruno Santos
"""
import sys, os
import pytest
import asyncio
from typing import Generator, Dict, Any
from sqlalchemy.orm import Session

# Add the main API directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# TestContainers imports
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

# Project imports
from config import get_settings, Settings
from infrastructure.persistence.database import Database
from infrastructure.persistence.base import Base
from tests.utils import apply_migrations


# TestContainers fixtures
@pytest.fixture(scope="session")
def postgres_container():
    """
    Create a PostgreSQL container for testing.
    
    This fixture uses TestContainers to create an ephemeral PostgreSQL container 
    for integration tests. The container is destroyed when the session ends.
    
    Returns:
        PostgresContainer: The PostgreSQL container instance
    """
    with PostgresContainer("postgres:13") as postgres:
        # Start the container
        postgres.start()
        
        # Yield the container
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    """
    Create a Redis container for testing.
    
    This fixture uses TestContainers to create an ephemeral Redis container
    for integration tests. The container is destroyed when the session ends.
    
    Returns:
        RedisContainer: The Redis container instance
    """
    with RedisContainer("redis:6") as redis:
        # Start the container
        redis.start()
        
        # Yield the container
        yield redis


@pytest.fixture(scope="session")
def test_settings(postgres_container, redis_container) -> Settings:
    """
    Create test settings with TestContainers connection strings.
    
    Args:
        postgres_container: PostgreSQL container fixture
        redis_container: Redis container fixture
        
    Returns:
        Settings: Configuration settings for tests
    """
    # Get default settings
    settings = get_settings()
    
    # Override with test container settings
    pg_port = postgres_container.get_exposed_port(5432)
    pg_host = postgres_container.get_container_host_ip()
    settings.database_url = f"postgresql://postgres:postgres@{pg_host}:{pg_port}/yvs_test"
    
    redis_port = redis_container.get_exposed_port(6379)
    redis_host = redis_container.get_container_host_ip()
    settings.redis_url = f"redis://{redis_host}:{redis_port}/0"
    
    # Set test environment
    settings.environment = "test"
    settings.debug = True
    
    return settings


@pytest.fixture(scope="session")
def test_db(postgres_container, test_settings) -> Database:
    """
    Create test database connection.
    
    Args:
        postgres_container: PostgreSQL container fixture
        test_settings: Test settings fixture
        
    Returns:
        Database: Database instance for tests
    """
    # Create database instance with test settings
    db = Database(db_url=test_settings.database_url)
    
    # Create all tables
    Base.metadata.create_all(bind=db.engine)
    
    # Apply migrations
    apply_migrations(test_settings.database_url)
    
    return db


@pytest.fixture(scope="function")
def db_session(test_db) -> Generator[Session, None, None]:
    """
    Create a clean database session for each test function.
    
    Args:
        test_db: Test database fixture
        
    Returns:
        Session: SQLAlchemy session for tests
    """
    # Create a fresh session
    session = test_db.SessionLocal()
    
    try:
        # Return the session for the test to use
        yield session
    finally:
        # Rollback any changes and close the session
        session.rollback()
        session.close()


# Async fixtures for FastAPI tests
@pytest.fixture(scope="session")
def event_loop():
    """Override default event loop for pytest-asyncio."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client(test_settings):
    """
    Create a FastAPI test client.
    
    Args:
        test_settings: Test settings fixture
        
    Returns:
        TestClient: FastAPI test client
    """
    # Lazy import to avoid circular dependencies
    from fastapi.testclient import TestClient
    from main import app
    
    # Create a test client with overridden dependencies
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def mock_settings(monkeypatch, test_settings):
    """
    Monkeypatch the global settings for tests.
    
    Args:
        monkeypatch: pytest's monkeypatch fixture
        test_settings: Test settings fixture
        
    Returns:
        Settings: Test settings object
    """
    # Import the get_settings function to patch
    from config import get_settings as original_get_settings
    
    # Create a function that returns our test settings
    def _get_test_settings():
        return test_settings
    
    # Patch the get_settings function
    monkeypatch.setattr("config.get_settings", _get_test_settings)
    
    # Return the test settings
    return test_settings
