# Running Tests in YouTube Video Summarizer

## Overview

The YouTube Video Summarizer project uses a multi-tiered testing approach with:
1. Fast unit tests that use mocks (no external dependencies)
2. Integration tests using TestContainers for isolated environments
3. End-to-end tests for complete system verification

This guide explains how to run each type of test.

## Prerequisites

- Python 3.10 or higher
- Required packages installed (`pip install -r api/requirements.txt`)
- Docker installed and running (for integration tests only)

## Test Categories

### Unit Tests

Unit tests focus on individual components in isolation, using mocks to replace external dependencies:

- **No external dependencies** like databases or Redis
- **Very fast** execution (milliseconds per test)
- **Easily runnable** on any environment
- **Ideal for development** and quick feedback

```bash
# Run all unit tests
cd api
python -m pytest tests/unit

# Run specific unit tests
python -m pytest tests/unit/auth
python -m pytest tests/unit/services/test_summary_generation_service.py
```

### Integration Tests

Integration tests verify how components interact with actual infrastructure using TestContainers:

- **Require Docker** to be running
- Create **ephemeral containers** for each test session
- Provide **isolated environments** for testing
- Test real interactions with databases and Redis

```bash
# Run all integration tests
cd api
python -m pytest tests/integration

# Run specific integration tests
python -m pytest tests/integration/repositories
python -m pytest tests/integration/caching/test_redis_cache.py
```

### End-to-End Tests

E2E tests verify complete user flows through the entire application:

- Test the **complete application stack**
- Require the **full application** to be running
- Provide validation of **full user journeys**

```bash
# Run all E2E tests
cd api
python -m pytest tests/e2e
```

## Running Tests with Markers

The project uses pytest markers to categorize tests:

```bash
# Run tests with specific markers
python -m pytest -m unit            # Run all unit tests
python -m pytest -m integration     # Run all integration tests
python -m pytest -m "not slow"      # Skip slow tests
```

Available markers:
- `unit`: Unit tests (no external dependencies)
- `integration`: Integration tests (requires Docker)
- `slow`: Tests that take longer to run
- `external`: Tests that require external services

## Combining Test Commands

You can combine various pytest options:

```bash
# Run unit tests with detailed output
python -m pytest tests/unit -v

# Run integration tests with a specific marker and output to JUnit format
python -m pytest tests/integration -m "not slow" --junitxml=test-results.xml

# Run specific test with debugging information
python -m pytest tests/unit/auth/test_token_encryption.py -v --no-header
```

## Test Infrastructure

### Unit Test Infrastructure

Unit tests use mock objects defined in `tests/unit/conftest.py`:
- Mock database sessions
- Mock Redis clients
- Mock settings
- Mock event publishers
- Mock repositories

### Integration Test Infrastructure

Integration tests use TestContainers defined in `tests/conftest.py`:
- PostgreSQL container with migrations applied
- Redis container
- Test settings pointing to containers
- Database sessions connected to test databases

## Guidelines for Writing Tests

### Unit Tests

1. Always use mocks for external dependencies
2. Focus on a single component/function
3. Avoid using actual database or Redis
4. Use the fixtures provided in `tests/unit/conftest.py`

Example unit test:
```python
def test_user_service(mock_database_session, mock_event_publisher):
    # Setup
    user_repo = MagicMock()
    user_service = UserService(user_repo, mock_event_publisher)
    
    # Test logic
    # ...
```

### Integration Tests

1. Use the TestContainers fixtures
2. Test interactions between components
3. Verify data persistence and retrieval
4. Clean up data after tests

Example integration test:
```python
def test_user_repository(db_session):
    # Setup
    repo = UserRepository(db_session)
    
    # Test actual database operations
    # ...
```

## Troubleshooting

### Unit Tests

**Problem**: Import errors in unit tests  
**Solution**: Ensure the project root is in PYTHONPATH

**Problem**: Mocks not working correctly  
**Solution**: Check that the mock fixture is being used correctly

### Integration Tests

**Problem**: "Docker not found" errors  
**Solution**: Ensure Docker is running

**Problem**: "Port already in use" errors  
**Solution**: Stop any other containers using the same ports

**Problem**: Database migration errors  
**Solution**: Check if migrations are applied correctly

## CI/CD Integration

The project uses GitHub Actions to run tests in CI/CD:

1. Unit tests run on every pull request
2. Integration tests run on merges to main branch
3. End-to-end tests run before releases

## Author

Bruno Santos
