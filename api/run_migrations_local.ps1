# Run migrations with local database configuration
Write-Host "Running database migrations with local configuration..." -ForegroundColor Green

# Copy local environment file to both directories
# - Root directory (for imports)
# - API directory (for local command execution)
if (Test-Path ../.env) {
    # Backup existing .env if it exists
    if (Test-Path ../.env.bak) {
        Remove-Item ../.env.bak
    }
    Move-Item ../.env ../.env.bak
    Write-Host "Backed up existing root .env to .env.bak" -ForegroundColor Yellow
}

if (Test-Path .env) {
    # Backup existing .env if it exists
    if (Test-Path .env.bak) {
        Remove-Item .env.bak
    }
    Move-Item .env .env.bak
    Write-Host "Backed up existing api .env to .env.bak" -ForegroundColor Yellow
}

# Copy local environment to both locations
Copy-Item ../.env.local ../.env
Copy-Item ../.env.local .env
Write-Host "Using local environment from .env.local" -ForegroundColor Yellow

# Directly set the database URL for Alembic to use
$envContent = Get-Content "../.env.local" -Raw
$databaseUrlMatch = [regex]::Match($envContent, "DATABASE_URL=(.*)")
if ($databaseUrlMatch.Success) {
    $databaseUrl = $databaseUrlMatch.Groups[1].Value
    Write-Host "Found database URL: $databaseUrl" -ForegroundColor Green

    # Create a temporary alembic.ini with the direct database URL
    $alembicContent = Get-Content "alembic.ini" -Raw
    $updatedAlembicContent = $alembicContent -replace "sqlalchemy.url = .*", "sqlalchemy.url = $databaseUrl"
    Set-Content "alembic.ini.temp" $updatedAlembicContent

    # Run alembic with the temporary config
    try {
        Write-Host "Running migrations..." -ForegroundColor Cyan
        alembic -c alembic.ini.temp upgrade head
        Write-Host "Migrations completed successfully." -ForegroundColor Green
    }
    catch {
        Write-Host "Migration failed: $_" -ForegroundColor Red
    }
    finally {
        # Clean up
        if (Test-Path "alembic.ini.temp") {
            Remove-Item "alembic.ini.temp"
        }
    }
}
else {
    Write-Host "Could not find DATABASE_URL in .env.local file" -ForegroundColor Red
}

# Restore original .env files if they existed
if (Test-Path ../.env.bak) {
    Remove-Item ../.env
    Move-Item ../.env.bak ../.env
    Write-Host "Restored original root .env" -ForegroundColor Yellow
}

if (Test-Path .env.bak) {
    Remove-Item .env
    Move-Item .env.bak .env
    Write-Host "Restored original api .env" -ForegroundColor Yellow
}
