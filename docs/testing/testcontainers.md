# TestContainers Implementation

## Overview

The YouTube Video Summarizer project uses TestContainers for Python to create isolated, ephemeral test environments for integration testing. This document explains how TestContainers are implemented and used in the project.

## TestContainers vs Unit Tests

The project uses two distinct testing approaches:

1. **Unit Tests**: Fast tests using mocks, with no infrastructure dependencies
2. **Integration Tests**: Tests using TestContainers for real infrastructure testing

TestContainers are only used for integration tests, not for unit tests. This separation ensures:
- Unit tests remain fast and can run without Docker
- Integration tests provide real-world validation with actual infrastructure

## Advantages of TestContainers

- **True Isolation**: Each test run gets its own dedicated containers
- **No Test Pollution**: Tests always run against clean databases
- **Consistency**: Tests behave the same on all environments (local, CI/CD)
- **Simplicity**: No manual setup or cleanup required
- **Reliability**: Tests are less likely to fail due to environment issues
- **Portability**: Works on any system with Docker, regardless of host OS

## Implementation Details

### Core Components

1. **Pytest Fixtures**: TestContainers are implemented as pytest fixtures in `api/tests/conftest.py`
2. **Database Migrations**: Automatic migration application for test databases
3. **Configuration Override**: Test-specific settings that point to the ephemeral containers

### Key Files

- `api/tests/conftest.py`: Contains all TestContainers fixtures and configuration
- `api/tests/utils/migrations.py`: Utilities for applying migrations to test databases
- `api/tests/integration/examples/test_testcontainers_example.py`: Example test demonstrating TestContainers usage

## Using TestContainers in Tests

### Basic Usage

To use TestContainers in an integration test:

```python
@pytest.mark.integration
def test_repository_function(db_session, test_settings):
    # Test code here that uses real PostgreSQL database
    repository = UserRepository(db_session)
    user = repository.create(User(email="test@example.com"))
    
    # Direct database verification
    assert user.id is not None
```

### Available Fixtures

The following TestContainers fixtures are available for integration tests:

- `postgres_container`: Raw PostgreSQL container instance
- `redis_container`: Raw Redis container instance
- `test_settings`: Application settings configured for test containers
- `test_db`: Database instance connected to the test database
- `db_session`: SQLAlchemy session for database operations (function-scoped)
- `client`: FastAPI TestClient configured with test dependencies
- `mock_settings`: Settings patched into the application for testing

### Container Lifecycle

TestContainers follows this lifecycle:

1. **Creation**: Containers are created when the fixture is first requested
2. **Initialization**: Database migrations are applied automatically
3. **Usage**: Tests interact with the containers
4. **Cleanup**: Containers are automatically stopped and removed when the fixture goes out of scope

## Technical Requirements

- Docker must be running to execute integration tests
- Python 3.10+ and pytest
- TestContainers packages (`testcontainers`, `testcontainers-postgres`, `testcontainers-redis`)

## Example Workflow

A typical integration test workflow using TestContainers:

```
Test execution starts
↓
pytest loads fixtures from conftest.py
↓
TestContainers creates PostgreSQL and Redis containers
↓
Migrations are applied to the test database
↓
Test functions execute using the containers
↓
Test execution completes
↓
TestContainers destroys the containers
```

## Testing Repository Classes

Repository classes are an ideal candidate for integration testing with TestContainers:

```python
@pytest.mark.integration
class TestUserRepository:
    """Integration tests for UserRepository"""
    
    def test_create_user(self, db_session):
        """Test creating a user in the database"""
        # Create a repository with the test session
        repository = UserRepository(db_session)
        
        # Create and persist a user
        user = User(email="test@example.com", display_name="Test User")
        created_user = repository.create(user)
        
        # Verify the user was created with an ID
        assert created_user.id is not None
        
        # Verify it can be retrieved
        retrieved_user = repository.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
```

## Testing Redis Cache

TestContainers can also be used to test Redis cache implementations:

```python
@pytest.mark.integration
class TestRedisCache:
    """Integration tests for Redis cache service"""
    
    @pytest.fixture
    async def redis_cache(self, redis_container):
        """Create a Redis cache instance connected to the test container"""
        redis_url = f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}"
        cache = RedisCache(redis_url)
        await cache.init()
        yield cache
        await cache.close()
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, redis_cache):
        """Test setting and getting a value from Redis"""
        # Test Redis operations with real Redis instance
        await redis_cache.set("test-key", "test-value")
        result = await redis_cache.get("test-key")
        assert result == "test-value"
```

## Best Practices

1. **Mark Integration Tests**: Always use the `@pytest.mark.integration` marker for tests using TestContainers
2. **Use Function-Scoped Sessions**: Use the `db_session` fixture which is function-scoped for isolation
3. **Keep Tests Independent**: Avoid dependencies between tests; each test should setup its own data
4. **Clean Up After Tests**: Ensure any created data is cleaned up (the session rollback helps with this)
5. **Don't Mix with Unit Tests**: Keep integration tests separate from unit tests

## Author

Bruno Santos
