# Script to help configure Neon PostgreSQL connection for local development
Write-Host "Neon PostgreSQL Connection Configuration Helper" -ForegroundColor Green
Write-Host "------------------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "This script will help you update your .env.local file with Neon PostgreSQL connection info." -ForegroundColor Cyan
Write-Host ""

# Get Neon connection details from user
$neonHost = Read-Host "Enter your Neon host (e.g., ep-cool-grass-123456.us-east-2.aws.neon.tech)"
$neonDatabase = Read-Host "Enter your database name (default: yvs_dev)" 
if ([string]::IsNullOrWhiteSpace($neonDatabase)) {
    $neonDatabase = "yvs_dev"
}
$neonUser = Read-Host "Enter your Neon username (default: postgres)"
if ([string]::IsNullOrWhiteSpace($neonUser)) {
    $neonUser = "postgres"
}
$neonPassword = Read-Host "Enter your Neon password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($neonPassword)
$passwordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Build the connection string
$connectionString = "postgresql://$neonUser`:$passwordText@$neonHost/$neonDatabase?sslmode=require"

# Update the .env.local file
$envContent = Get-Content ".env.local" -Raw
$updatedContent = $envContent -replace "DATABASE_URL=.*", "DATABASE_URL=$connectionString"
Set-Content ".env.local" $updatedContent

Write-Host ""
Write-Host "Your .env.local file has been updated with the Neon connection string!" -ForegroundColor Green
Write-Host "You can now run migrations using the updated connection info:" -ForegroundColor Yellow
Write-Host "  cd api" -ForegroundColor Yellow
Write-Host "  ./run_migrations_local.ps1" -ForegroundColor Yellow
