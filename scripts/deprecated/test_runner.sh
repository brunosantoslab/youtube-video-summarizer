#!/bin/bash
# YouTube Video Summarizer Test Runner
# Author: Bruno Santos
#
# This script automates the setup and execution of both unit and integration tests
# for the YouTube Video Summarizer project.

set -e

# Terminal output colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions for displaying status messages
log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker_running() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if containers are running
check_containers_running() {
    if ! docker-compose ps | grep -q "api.*Up"; then
        log_info "Containers are not running. Starting containers..."
        docker-compose up -d
        
        # Wait for containers to initialize
        log_info "Waiting for containers to initialize..."
        sleep 10
    else
        log_info "Containers are already running"
    fi
}

# Check and create test database
setup_test_database() {
    log_info "Checking test database..."
    
    # Check if test database exists, create if not
    docker-compose exec -T db psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'yvs_test'" | grep -q 1 || \
        (log_info "Creating test database..." && \
         docker-compose exec -T db psql -U postgres -c "CREATE DATABASE yvs_test")
    
    log_success "Test database ready"
}

# Run database migrations
run_migrations() {
    log_info "Running migrations on main database..."
    docker-compose exec -T api alembic upgrade head
    
    log_info "Running migrations on test database..."
    docker-compose exec -T api bash -c "DATABASE_URL=postgresql://postgres:postgres@db:5432/yvs_test alembic upgrade head"
    
    log_success "Migrations completed"
}

# Function to run specific tests
run_specific_tests() {
    test_path=$1
    log_info "Running tests: $test_path"
    docker-compose exec -T api pytest $test_path -v
    
    if [ $? -eq 0 ]; then
        log_success "Tests in $test_path completed successfully"
    else
        log_error "Tests failed in $test_path"
        exit_code=1
    fi
}

# Variable to track test success
exit_code=0

# Main function
main() {
    log_info "=== STARTING TEST EXECUTION ==="
    
    # Check Docker
    check_docker_running
    
    # Start containers if needed
    check_containers_running
    
    # Setup test database
    setup_test_database
    
    # Run migrations
    run_migrations
    
    # Determine which tests to run based on arguments
    if [ "$1" = "all" ] || [ -z "$1" ]; then
        # Run all tests
        log_info "Running all tests..."
        
        # Unit tests
        run_specific_tests "tests/unit"
        
        # Integration tests
        run_specific_tests "tests/integration"
        
    elif [ "$1" = "unit" ]; then
        # Run only unit tests
        run_specific_tests "tests/unit"
        
    elif [ "$1" = "integration" ]; then
        # Run only integration tests
        run_specific_tests "tests/integration"
        
    else
        # Run specific test path
        run_specific_tests "$1"
    fi
    
    log_info "=== TEST EXECUTION COMPLETED ==="
    
    # Return appropriate exit code
    exit $exit_code
}

# Execute the main function with all arguments
main "$@"
