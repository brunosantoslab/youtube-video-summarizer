# Run Unit Tests with Test Environment
Write-Host "Running Unit Tests with Test Environment..." -ForegroundColor Green

# Copy test environment file to .env for testing
if (Test-Path .env) {
    # Backup existing .env if it exists
    if (Test-Path .env.bak) {
        Remove-Item .env.bak
    }
    Move-Item .env .env.bak
    Write-Host "Backed up existing .env to .env.bak" -ForegroundColor Yellow
}

# Copy test environment
Copy-Item .env.test .env
Write-Host "Using test environment from .env.test" -ForegroundColor Yellow

# Run pytest
python -m pytest tests/unit -v

# Restore original .env if it existed
if (Test-Path .env.bak) {
    Remove-Item .env
    Move-Item .env.bak .env
    Write-Host "Restored original .env" -ForegroundColor Yellow
}

Write-Host "Test execution completed." -ForegroundColor Green
