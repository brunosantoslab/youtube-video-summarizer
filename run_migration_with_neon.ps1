# Clear script for running migrations with Neon PostgreSQL settings
Write-Host "Setting up migration environment for Neon PostgreSQL..." -ForegroundColor Green

# Copy .env.local to api directory
Copy-Item .env.local api/.env -Force
Write-Host "Copied .env.local to api/.env" -ForegroundColor Cyan

# Clear any potential cached settings by using a fresh Python process
Write-Host "Running migration with fresh environment..." -ForegroundColor Cyan
cd api
python -c "from alembic import command; from alembic.config import Config; cfg = Config('alembic.ini'); command.upgrade(cfg, 'head')"

# Migration status
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Migration failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Try restarting your IDE to clear any cached environment variables!" -ForegroundColor Yellow
}
