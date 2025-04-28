# YouTube Video Summarizer - Install Dependencies
Write-Host "Installing YouTube Video Summarizer dependencies..." -ForegroundColor Green

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install base requirements
Write-Host "Installing base requirements..." -ForegroundColor Yellow
python -m pip install -r .\api\requirements.txt

# Install TestContainers with PostgreSQL and Redis extras
Write-Host "Installing TestContainers with extras..." -ForegroundColor Yellow
python -m pip install "testcontainers[postgres,redis]"

# Install cryptography explicitly (important for authentication)
Write-Host "Installing cryptography..." -ForegroundColor Yellow
python -m pip install cryptography

# Verify installations
Write-Host "Verifying critical dependencies..." -ForegroundColor Yellow
python -c "import cryptography; print(f'Cryptography installed: {cryptography.__version__}')"
python -c "import testcontainers; print(f'TestContainers installed: {testcontainers.__version__}')"

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "To run unit tests: cd api && python -m pytest tests/unit" -ForegroundColor Cyan
Write-Host "To run integration tests (requires Docker): cd api && python -m pytest tests/integration" -ForegroundColor Cyan
