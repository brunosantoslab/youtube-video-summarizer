# Direct migration with hardcoded connection string
Write-Host "Running migration directly with Neon PostgreSQL..." -ForegroundColor Green
Write-Host "Using connection string hardcoded in env.py - This should work!" -ForegroundColor Cyan

# Simply run alembic
alembic upgrade head

# Check status
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Migration failed with exit code: $LASTEXITCODE" -ForegroundColor Red
}
