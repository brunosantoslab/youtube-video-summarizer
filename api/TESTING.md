# Testing Guide for YouTube Video Summarizer

Author: Bruno Santos  
Date: April 29, 2025

This document describes the testing strategies for the YouTube Video Summarizer project.

## Test Levels

### Unit Tests

Unit tests focus on testing components in isolation:

```bash
cd api
python -m pytest tests/unit
```

### Integration Tests

#### With Docker (Recommended)

Integration tests use TestContainers to create ephemeral environments:

```bash
cd api
python -m pytest tests/integration
```

#### Without Docker (Using Neon PostgreSQL)

To run integration tests without Docker, using the Neon PostgreSQL database:

```bash
cd api
.\run_tests_without_docker.ps1
```

**Note**: The class naming has been standardized. The repository is correctly referred to as `PostgresSummaryRepository` in all tests.

## Docker Requirements

- When running with Docker, ensure Docker Desktop is running
- When running without Docker, ensure the Neon PostgreSQL connection string is correctly set in the environment variables

## Migration Structure

Database migrations follow this sequence:

1. `20250426001` - Users table
2. `001_oauth_tokens` - OAuth tokens table
3. `0015_videos` - Videos table
4. `002_transcripts` - Transcripts table
5. `202504260001` - Metadata field renaming
6. `003_tasks` - Processing tasks table
7. `004_summaries` - Summaries and saved_summaries tables
8. `005_topics` - Topics table
9. `006_ai_cache` - AI cache and AI usage tables

## Applying Migrations

To apply all migrations:

```bash
cd api
alembic upgrade head
```

To apply up to a specific migration:

```bash
cd api
alembic upgrade <revision_id>
```

## Troubleshooting

- **TestContainers**: Requires Docker installed and running
- **Import Errors**: Verify class names in the corresponding files
- **Database Errors**: Check credentials and connection to Neon PostgreSQL database
- **Port Conflicts**: Verify no other services are using the same ports
- **Docker Connection Issues**: Make sure Docker is running if using TestContainers

## Next Steps

The next logical task is the implementation of [YVS-12] Frontend Architecture Development, which will be started in a new context.
