# Testing Guide for YouTube Video Summarizer

This document provides a quick reference for running tests in the YouTube Video Summarizer project.

## Prerequisites

1. Install the required packages:
   ```bash
   # Install the base requirements
   pip install -r requirements.txt
   
   # Install TestContainers core with PostgreSQL and Redis extras
   pip install "testcontainers[postgres,redis]"
   ```

2. Configure environment:
   - Copy `.env.test` to `.env` for testing, or
   - Use the provided test runners that handle this automatically

3. Ensure Docker is running (required for integration tests only)

4. System dependencies (especially important for WSL/Linux):
   - SQLite development libraries (required for test coverage reporting)
   ```bash
   # Ubuntu/Debian/WSL
   sudo apt-get install -y libsqlite3-dev
   
   # Alternatively, install the pysqlite3 package
   pip install pysqlite3
   ```
   
   For more details on system dependencies, see [system dependencies](/docs/setup/system_dependencies.md)

## Running Tests

### Using Convenience Scripts

We provide scripts that handle environment setup automatically:

```bash
# In PowerShell
.\run_unit_tests.ps1

# Or in CMD
run_unit_tests.bat
```

### Manual Test Execution

#### Unit Tests (No Docker Required)

```bash
# Run all unit tests
python -m pytest tests/unit

# Run specific unit test modules
python -m pytest tests/unit/auth
python -m pytest tests/unit/services/test_summary_generation_service.py
```

#### Integration Tests (Docker Required)

```bash
# Run all integration tests
python -m pytest tests/integration

# Run specific integration test modules
python -m pytest tests/integration/repositories
```

## Test Categories

### Unit Tests
- Test individual components in isolation
- Use mocks for external dependencies
- Very fast execution (milliseconds)
- Don't require Docker or infrastructure
- Use fixtures from `tests/unit/conftest.py`

### Integration Tests
- Verify interactions between components
- Use TestContainers for real infrastructure
- Require Docker to be running
- Create ephemeral containers for testing
- Use fixtures from `tests/conftest.py`

## Useful Commands

### Run Tests with Specific Markers

```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Skip slow tests
python -m pytest -m "not slow"
```

### Test Coverage

```bash
# Generate coverage report
python -m pytest --cov=api

# Generate HTML coverage report
python -m pytest --cov=api --cov-report=html
```

### Parallel Test Execution

```bash
# Run tests in parallel
python -m pytest -xvs
```

### Verbose Output

```bash
# Run with detailed output
python -m pytest -v
```

## Troubleshooting

### Configuration Issues

If you encounter errors related to missing environment variables:
- Ensure you have a valid `.env` file in the api directory
- Use the provided `.env.test` as a template
- Try using the test runner scripts that handle environment setup

### TestContainers Installation Issues

If you encounter errors installing testcontainers:

```bash
# Install TestContainers with extras
pip install "testcontainers[postgres,redis]"
```

### SQLite Issues for Coverage Tests

Se você encontrar erros relacionados ao SQLite durante os testes de cobertura (coverage), especialmente em ambientes WSL/Linux:

```
ModuleNotFoundError: No module named '_sqlite3'
```

Você pode usar o script de configuração fornecido:

```bash
# Configure o ambiente para SQLite
python -m api.scripts.setup_sqlite_for_testing

# Para executar testes com o patch do SQLite
python -m api.scripts.coverage_sqlite_patch -m pytest tests/unit
```

Este script irá:
1. Verificar se o SQLite está disponível
2. Instalar o pacote pysqlite3 se necessário
3. Criar um patch para substituir o módulo sqlite3 durante os testes
4. Fornecer instruções para solução permanente

A solução permanente é instalar as bibliotecas de desenvolvimento do SQLite:

```bash
sudo apt-get install -y libsqlite3-dev
```

E então reinstalar o Python ou usar Docker para desenvolvimento.

### Docker Not Running

If you see errors about Docker not being available:

```
docker.errors.DockerException: Error while fetching server API version
```

Ensure Docker is running and you have permission to access it.

### Port Conflicts

If you see errors about ports already in use, TestContainers will attempt to use different ports automatically. However, if you have many Docker containers running, consider stopping unused containers.

## Adding New Tests

### Unit Tests

Add new unit tests in `tests/unit/` directory:

```python
# tests/unit/your_module/test_your_feature.py

def test_your_feature(mock_database_session, mock_event_publisher):
    # Use the mock fixtures from tests/unit/conftest.py
    # ...
```

### Integration Tests

Add new integration tests in `tests/integration/` directory:

```python
# tests/integration/your_module/test_your_feature.py

@pytest.mark.integration
def test_your_feature(db_session, test_settings):
    # Use the TestContainers fixtures from tests/conftest.py
    # ...
```

## Documentation

For more detailed documentation on the testing approach, see:
- `docs/testing/running_tests.md`: Complete guide to running tests
- `docs/testing/testcontainers.md`: Details on TestContainers implementation
- `docs/testing/migration_guide.md`: Guide for migrating tests to new approach
