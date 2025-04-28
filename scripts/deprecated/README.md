# Deprecated Scripts

These scripts have been deprecated following the migration to TestContainers for testing infrastructure.

## Deprecated Files

- `setup_docker_test_env.sh`: Previously used to set up Docker test environment
- `test_runner.sh`: Linux/Mac script for running tests
- `test_runner.bat`: Windows script for running tests

## Reason for Deprecation

These scripts were part of the previous test infrastructure that required manual setup of Docker containers and test environments. With the migration to TestContainers (completed in task YVS-21), test containers are now created and managed automatically by the test framework.

## New Test Approach

Tests are now run using pytest with TestContainers:

```bash
cd api
python -m pytest
```

See the following documentation for more details:
- `/docs/testing/testcontainers.md`
- `/docs/testing/running_tests.md`

## Author

Bruno Santos
