# Deprecated Files for Removal

The following files are no longer needed after the migration to TestContainers and should be removed from the project:

## Scripts

- `scripts/setup_docker_test_env.sh`: Setup script for test environment
- `scripts/test_runner.sh`: Linux/Mac test runner script
- `scripts/test_runner.bat`: Windows test runner script

## Docker Configuration

The existing docker-compose.yml file does not need to be modified as it will still be used for development. TestContainers creates its own ephemeral containers for testing without affecting this configuration.

## Why These Files Are No Longer Needed

These scripts were used to:
1. Set up a static test database
2. Run migrations on the test database
3. Execute tests against that database

With TestContainers, these tasks are now handled automatically:
1. Ephemeral containers are created for each test session
2. Migrations are applied automatically via the migration utilities
3. Tests use the fixtures defined in conftest.py

## Removal Procedure

1. Ensure all tests are passing with the new TestContainers approach
2. Remove the deprecated files:
   ```bash
   rm scripts/setup_docker_test_env.sh
   rm scripts/test_runner.sh
   rm scripts/test_runner.bat
   ```
3. Update any documentation or CI/CD pipelines that referenced these files

## Author

Bruno Santos
```
