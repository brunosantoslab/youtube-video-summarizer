@echo off
REM YouTube Video Summarizer Test Runner
REM Author: Bruno Santos
REM
REM This script automates the setup and execution of both unit and integration tests
REM for the YouTube Video Summarizer project on Windows systems.

SETLOCAL EnableDelayedExpansion

REM Set colors for Windows terminal
SET GREEN=[92m
SET YELLOW=[93m
SET RED=[91m
SET NC=[0m

REM Functions for displaying status messages
:log_info
echo %YELLOW%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Check if Docker is running
:check_docker_running
docker info > nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log_error "Docker is not running. Please start Docker and try again."
    exit /b 1
)
goto :eof

REM Check if containers are running
:check_containers_running
docker-compose ps | findstr "api.*Up" > nul
if %ERRORLEVEL% neq 0 (
    call :log_info "Containers are not running. Starting containers..."
    docker-compose up -d
    
    REM Wait for containers to initialize
    call :log_info "Waiting for containers to initialize..."
    timeout /t 10 /nobreak > nul
) else (
    call :log_info "Containers are already running"
)
goto :eof

REM Check and create test database
:setup_test_database
call :log_info "Checking test database..."

REM Check if test database exists, create if not
docker-compose exec -T db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'yvs_test'" | findstr "1" > nul
if %ERRORLEVEL% neq 0 (
    call :log_info "Creating test database..."
    docker-compose exec -T db psql -U postgres -c "CREATE DATABASE yvs_test"
)

call :log_success "Test database ready"
goto :eof

REM Run database migrations
:run_migrations
call :log_info "Running migrations on main database..."
docker-compose exec -T api alembic upgrade head

call :log_info "Running migrations on test database..."
docker-compose exec -T api bash -c "DATABASE_URL=postgresql://postgres:postgres@db:5432/yvs_test alembic upgrade head"

call :log_success "Migrations completed"
goto :eof

REM Function to run specific tests
:run_specific_tests
call :log_info "Running tests: %~1"
docker-compose exec -T api pytest %~1 -v

if %ERRORLEVEL% equ 0 (
    call :log_success "Tests in %~1 completed successfully"
) else (
    call :log_error "Tests failed in %~1"
    set exit_code=1
)
goto :eof

REM Main function
:main
call :log_info "=== STARTING TEST EXECUTION ==="

REM Initialize exit code
set exit_code=0

REM Check Docker
call :check_docker_running

REM Start containers if needed
call :check_containers_running

REM Setup test database
call :setup_test_database

REM Run migrations
call :run_migrations

REM Determine which tests to run based on arguments
if "%~1"=="all" (
    goto :run_all_tests
) else if "%~1"=="" (
    goto :run_all_tests
) else if "%~1"=="unit" (
    call :run_specific_tests "tests/unit"
) else if "%~1"=="integration" (
    call :run_specific_tests "tests/integration"
) else (
    call :run_specific_tests "%~1"
)

call :log_info "=== TEST EXECUTION COMPLETED ==="

exit /b %exit_code%

:run_all_tests
call :log_info "Running all tests..."
call :run_specific_tests "tests/unit"
call :run_specific_tests "tests/integration"
goto :eof

REM Execute main with all arguments
call :main %*
