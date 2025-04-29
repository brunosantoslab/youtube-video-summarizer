#!/bin/bash
# YouTube Video Summarizer Docker Test Environment Setup
# Author: Bruno Santos
#
# This script creates or updates necessary Docker files to support
# automated testing for the YouTube Video Summarizer project.

set -e

# Terminal output colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for displaying status messages
log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Main project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
API_DIR="${PROJECT_DIR}/api"

log_info "Setting up Docker test environment in ${PROJECT_DIR}"

# Step 1: Create API entrypoint script
log_step "Creating API entrypoint script"

mkdir -p "${PROJECT_DIR}/api/scripts"
cat > "${PROJECT_DIR}/api/scripts/entrypoint.sh" << 'EOF'
#!/bin/bash
# API Docker Entrypoint Script
# Author: Bruno Santos

set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -U postgres -q; do
    sleep 1
done
echo "PostgreSQL is up!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! redis-cli -h redis ping > /dev/null 2>&1; do
    sleep 1
done
echo "Redis is up!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
if [ "$1" = "test" ]; then
    # Start in test mode (no server)
    echo "Test mode - not starting server"
    tail -f /dev/null
else
    # Start server normally
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
EOF

chmod +x "${PROJECT_DIR}/api/scripts/entrypoint.sh"
log_success "API entrypoint script created"

# Step 2: Update or create Dockerfile for API
log_step "Updating API Dockerfile"

cat > "${PROJECT_DIR}/api/Dockerfile" << 'EOF'
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install PostgreSQL client and Redis tools for healthchecks
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/scripts/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
EOF

log_success "API Dockerfile updated"

# Step 3: Update docker-compose.yml
log_step "Updating docker-compose.yml"

cat > "${PROJECT_DIR}/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=yvs
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: ./api
    volumes:
      - ./api:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - .env
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=yvs

volumes:
  postgres_data:
EOF

log_success "docker-compose.yml updated"

# Step 4: Create .env template if it doesn't exist
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    log_step "Creating .env template"
    
    cat > "${PROJECT_DIR}/.env" << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/yvs
DATABASE_TEST_URL=postgresql://postgres:postgres@db:5432/yvs_test

# Redis
REDIS_URL=redis://redis:6379/0

# YouTube API
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REDIRECT_URI=http://localhost:8000/api/auth/youtube/callback

# AI Providers
OPENAI_API_KEY=your_openai_key_here
GOOGLE_AI_API_KEY=your_google_ai_key_here

# Application
SECRET_KEY=testing_secret_key_replace_in_production
DEBUG=true
ENVIRONMENT=development
EOF

    log_success ".env template created"
    log_info "⚠️ Please update the .env file with your actual API keys and credentials!"
else
    log_info ".env file already exists, not overwriting"
fi

# Final instructions
log_info ""
log_info "==== Docker Test Environment Setup Complete ===="
log_info ""
log_info "Next steps:"
log_info "1. Update the .env file with your API keys and credentials"
log_info "2. Run tests with: ./scripts/test_runner.sh [all|unit|integration]"
log_info ""
log_success "Setup completed successfully!"
