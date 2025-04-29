# Script to run tests without Docker
# Author: Bruno Santos

Write-Host "Running integration tests without Docker" -ForegroundColor Green

# Configure environment variables for tests
$env:PYTEST_SKIP_CONTAINERS = "true"
$env:DATABASE_URL = "postgresql://neondb_owner:npg_PS0NT6DzdvRn@ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech/summary_tube_db?sslmode=require"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:TEST_MODE = "no_docker"

# Run tests
try {
    python -m pytest -xvs tests/integration/repositories
}
finally {
    # Clean up environment variables
    Remove-Item Env:\PYTEST_SKIP_CONTAINERS -ErrorAction SilentlyContinue
    Remove-Item Env:\DATABASE_URL -ErrorAction SilentlyContinue
    Remove-Item Env:\REDIS_URL -ErrorAction SilentlyContinue
    Remove-Item Env:\TEST_MODE -ErrorAction SilentlyContinue
}
