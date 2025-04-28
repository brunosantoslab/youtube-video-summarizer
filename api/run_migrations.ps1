# Simple script to run migrations with .env.local
Write-Host "Running database migrations with Neon PostgreSQL..." -ForegroundColor Green

# Backup existing .env files if they exist
if (Test-Path .env) {
    Copy-Item .env .env.docker.bak
    Write-Host "Backed up .env to .env.docker.bak" -ForegroundColor Yellow
}

# Copy local environment file
Copy-Item ..\.env.local .env
Write-Host "Using Neon database configuration from .env.local" -ForegroundColor Yellow

# Run alembic
try {
    alembic upgrade head
    Write-Host "Migrations completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Migration failed: $_" -ForegroundColor Red
}
finally {
    # Restore original .env if backup exists
    if (Test-Path .env.docker.bak) {
        Copy-Item .env.docker.bak .env
        Remove-Item .env.docker.bak
        Write-Host "Restored original .env configuration" -ForegroundColor Yellow
    }
}
