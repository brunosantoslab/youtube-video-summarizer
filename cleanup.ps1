# Script to clean up temporary files and scripts
Write-Host "Cleaning up temporary files and scripts..." -ForegroundColor Green

# Project root scripts to delete
$rootScriptsToDelete = @(
    "apply_neon_migration.py",
    "get_neon_connection.ps1",
    "run_migration_with_neon.ps1",
    "README.md.updated"
)

# API directory scripts to delete
$apiScriptsToDelete = @(
    "check_migration_state.py",
    "direct_migration.py",
    "run_direct_migration.ps1",
    "run_migrations.ps1",
    "run_migrations_local.ps1",
    "run_migrations_neon.py",
    "run_neon_migration.py"
)

# Delete root scripts
foreach ($script in $rootScriptsToDelete) {
    $path = "$script"
    if (Test-Path $path) {
        Remove-Item $path
        Write-Host "Deleted: $path" -ForegroundColor Yellow
    }
}

# Delete API scripts
foreach ($script in $apiScriptsToDelete) {
    $path = "api\$script"
    if (Test-Path $path) {
        Remove-Item $path
        Write-Host "Deleted: $path" -ForegroundColor Yellow
    }
}

Write-Host "Cleanup complete!" -ForegroundColor Green
