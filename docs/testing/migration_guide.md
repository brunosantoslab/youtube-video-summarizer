# Migration Guide: Improved Testing Approach

## Overview

This guide outlines the migration from our previous script-based testing approach to a more structured testing strategy with:

1. **Pure Unit Tests**: Fast tests with no external dependencies
2. **Integration Tests with TestContainers**: For testing with real infrastructure in isolated environments

## Key Changes

### Before Migration

- Script-based test setup
- No clear distinction between unit and integration tests
- Manual database setup and cleanup
- Fixed test database configuration
- OS-specific test runners

### After Migration

- Clear separation between unit and integration tests
- Pure unit tests with no infrastructure dependencies
- Integration tests using TestContainers for ephemeral environments
- Pytest-driven test execution
- Cross-platform compatibility

## Benefits of the Migration

| Area | Before | After |
|------|--------|-------|
| **Speed** | Slower unit tests with infrastructure | Fast unit tests with mocks |
| **Isolation** | Shared test database | Ephemeral containers per test run |
| **Setup** | Manual script execution | Automatic container management |
| **Maintenance** | OS-specific scripts | Cross-platform pytest commands |
| **CI/CD** | Complex script integration | Simple pytest commands |

## Migration Steps

### 1. Update Dependencies

```bash
# Install required packages
pip install pytest pytest-asyncio testcontainers testcontainers-postgres testcontainers-redis
```

### 2. Update Directory Structure

Organize tests into clear categories:

```
tests/
├── unit/            # Unit tests - No external dependencies
├── integration/     # Integration tests - Using TestContainers
└── e2e/             # End-to-end tests - Full application stack
```

### 3. Create Separate Configuration Files

- `tests/conftest.py`: TestContainers setup for integration tests
- `tests/unit/conftest.py`: Mock-based setup for unit tests
- `tests/integration/conftest.py`: Additional integration-specific fixtures

### 4. Update Test Files

#### Unit Tests

Update unit tests to use mocks instead of real infrastructure:

```python
# Before
def test_function(db_session):
    # Using real database
    repository = UserRepository(db_session)
    # ...

# After
def test_function(mock_database_session):
    # Using mocked database
    repository = UserRepository(mock_database_session)
    # ...
```

#### Integration Tests

Update integration tests to use TestContainers:

```python
@pytest.mark.integration
def test_function(db_session):
    # db_session is connected to a TestContainers PostgreSQL instance
    repository = UserRepository(db_session)
    # ...
```

### 5. Remove Deprecated Scripts

The following scripts are no longer needed:

- `scripts/setup_docker_test_env.sh`
- `scripts/test_runner.sh`
- `scripts/test_runner.bat`

These have been moved to the `scripts/deprecated` directory for reference if needed.

### 6. Update CI/CD Pipeline

Update CI/CD configuration to use pytest directly:

```yaml
# Before
- run: ./scripts/test_runner.sh all

# After
- run: pytest tests/unit                   # Fast tests on every commit
- run: pytest tests/integration            # Infrastructure tests on main branch
```

## Running Tests After Migration

### Unit Tests (Fast, No Docker Required)

```bash
cd api
python -m pytest tests/unit
```

### Integration Tests (Requires Docker)

```bash
cd api
python -m pytest tests/integration
```

### All Tests

```bash
cd api
python -m pytest
```

### With Markers

```bash
cd api
python -m pytest -m unit           # Only unit tests
python -m pytest -m integration    # Only integration tests
```

## Troubleshooting

### Docker Connectivity Issues

**Problem**: Integration tests fail with Docker connection errors  
**Solution**: Ensure Docker is running and accessible

### Import Errors

**Problem**: ModuleNotFoundError in tests  
**Solution**: Ensure the current directory is in your PYTHONPATH (`export PYTHONPATH=$PYTHONPATH:.`)

### Test Discovery Issues

**Problem**: Tests not being found  
**Solution**: Ensure test files follow the naming convention `test_*.py`

## Author

Bruno Santos
