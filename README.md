# YouTube Video Summarizer

An intelligent assistant that helps you save time by automatically extracting and summarizing key topics from YouTube videos in your feed.

## Overview

YouTube Video Summarizer monitors your YouTube subscriptions for new videos, uses AI to analyze their content, and delivers concise summaries highlighting the most important topics. Instead of watching hours of content, get the key insights delivered directly to you.

## Features

- **Automated Feed Monitoring**: Continuously tracks your YouTube subscriptions for new content
- **AI-Powered Summarization**: Leverages advanced language models to identify and extract the most relevant information
- **Topic Extraction**: Intelligently categorizes video content into key topics and themes
- **Interactive Dashboard**: Clean, intuitive interface to browse and organize video summaries
- **Notebook Integration**: Easily view videos within notebook environments for research and analysis
- **YouTube Authentication**: Seamless integration with your existing YouTube account

## Tech Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: PostgreSQL (hosted on Neon)
- **Caching/Queue**: Redis
- **Background Processing**: Celery
- **Authentication**: OAuth2 with YouTube

### Frontend
- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **API Integration**: Axios

### AI Components
- **Transcription**: YouTube Captions API + Whisper API
- **Summarization**: OpenAI GPT-4, Google Gemini
- **Orchestration**: LangChain

### Infrastructure
- **Containerization**: Docker
- **Development**: Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: 
  - Fast unit tests with mocks
  - Integration tests with TestContainers for ephemeral environments

## Architecture

The application follows Clean Architecture with Domain-Driven Design principles:

1. **Domain Layer**: Core business entities and logic
2. **Application Layer**: Use cases and orchestration
3. **Infrastructure Layer**: External services and persistence
4. **Presentation Layer**: API controllers and frontend UI

### Key Components

- **Feed Monitor**: Checks for new videos in subscriptions
- **Video Processor**: Extracts and analyzes video content
- **AI Summarizer**: Generates concise summaries and extracts topics
- **Dashboard**: User interface for viewing and organizing summaries

### YouTube API Integration

The application integrates with YouTube APIs through several specialized components:

- **OAuth Authentication**: Secure authentication flow using OAuth 2.0 protocol
- **Channels API Client**: Retrieves subscription and channel data
- **Videos API Client**: Fetches video metadata and content
- **Captions API Client**: Extracts and processes video transcripts
- **API Service**: Comprehensive service combining all YouTube API operations

The authentication implementation includes:
- Token encryption for secure storage
- Automatic token refresh management
- Session integration with the application
- Comprehensive error handling and rate limit management

## Project Status

Current development status (as of April 29, 2025):

### Completed Components

- **Core Backend Infrastructure**: Domain model, repositories, database integration
- **YouTube API Integration**: Authentication, data fetching, and transcript extraction
- **AI Processing Pipeline**: Video processing, transcription, summarization, and topic extraction
- **Async Processing**: Background task processing with Celery and Redis
- **Testing Infrastructure**: Unit tests and integration tests with TestContainers

### In Progress

- **API Documentation**: Documenting API endpoints for frontend integration
- **Testing Completion**: Finalizing tests for YouTube API integration

### Next Steps

- Frontend development (React + TypeScript)
- Dashboard implementation
- User experience refinement

For detailed task tracking, see [Project Tasks](/docs/tasks/project_tasks.md)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- YouTube API credentials
- OpenAI API key (or other supported AI provider)
- Neon PostgreSQL database
- System dependencies for running tests (see [system dependencies](/docs/setup/system_dependencies.md))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-video-summarizer.git
   cd youtube-video-summarizer
   ```

2. Create a `.env` file with your configuration:
   ```
   # Database - Already configured for Docker environment
   DATABASE_URL=postgresql://postgres:postgres@db:5432/yvs
   
   # Redis - Already configured for Docker environment
   REDIS_URL=redis://redis:6379/0
   
   # YouTube API - You need to provide these values
   YOUTUBE_API_KEY=your_api_key
   YOUTUBE_CLIENT_ID=your_client_id
   YOUTUBE_CLIENT_SECRET=your_client_secret
   YOUTUBE_REDIRECT_URI=http://localhost:8000/api/auth/youtube/callback
   
   # AI Providers - You need to provide these values
   OPENAI_API_KEY=your_openai_key
   GOOGLE_AI_API_KEY=your_google_ai_key
   
   # Application - Already configured with defaults
   SECRET_KEY=your_secret_key
   DEBUG=true
   ENVIRONMENT=development
   ```

3. Start the development environment:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:3000

### Development Workflow

1. **Docker-Based Development** (recommended for full stack):
   ```bash
   # Start service in development mode
   docker-compose up -d
   
   # Generate migrations
   docker-compose exec api alembic revision --autogenerate -m "Description"
   
   # Apply migrations
   docker-compose exec api alembic upgrade head
   ```

2. **Local Development with Neon PostgreSQL** (without Docker):
   ```bash
   # Create a .env.local file with your Neon PostgreSQL connection string
   # DATABASE_URL=postgresql://username:password@your-neon-hostname/dbname?sslmode=require
   
   # Copy the environment file to the API directory
   cp .env.local api/.env
   
   # Navigate to the API directory
   cd api
   
   # Apply migrations (may need to restart IDE first to refresh environment)
   alembic upgrade head
   
   # Run tests
   python -m pytest tests/unit
   ```

3. **Frontend Development**:
   ```bash
   # Install dependencies
   cd frontend
   npm install
   
   # Start development server
   npm run dev
   ```

## Project Structure

```
.
├── api/                     # Backend API
│   ├── domain/              # Domain layer
│   │   ├── models/          # Domain entities
│   │   └── repositories/    # Repository interfaces
│   ├── application/         # Application services
│   │   ├── dtos/            # Data Transfer Objects
│   │   └── services/        # Business logic services
│   ├── infrastructure/      # External integrations
│   │   ├── auth/            # Authentication services
│   │   ├── persistence/     # Database ORM entities
│   │   ├── repositories/    # Repository implementations
│   │   └── youtube/         # YouTube API clients
│   └── presentation/        # API controllers
│       └── routes/          # API routes
├── frontend/                # React frontend
│   ├── public/              # Static assets
│   └── src/                 # Source code
├── tests/                   # Test suites
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── docker/                  # Docker configuration
├── docs/                    # Documentation
├── .github/                 # GitHub workflows
├── docker-compose.yml       # Development environment
└── README.md                # This file
```

## Testing

The project uses a comprehensive multi-level testing strategy:

### Running Tests

```bash
# Run all tests
cd api
python -m pytest

# Run only unit tests (fast, no Docker required)
python -m pytest tests/unit

# Run only integration tests (requires Docker)
python -m pytest tests/integration

# Run tests with specific markers
python -m pytest -m unit
python -m pytest -m integration

# Run specific test modules
python -m pytest tests/unit/auth
python -m pytest tests/integration/repositories
```

### Test Categories

#### Unit Tests

Unit tests focus on testing components in isolation without dependencies on external systems:
- Use mocking to replace external dependencies
- Very fast execution (milliseconds)
- Don't require Docker or any infrastructure
- Focus on correctness of individual components
- Run frequently during development

Example command:
```bash
cd api
python -m pytest tests/unit
```

#### Integration Tests

Integration tests verify how components work together using real infrastructure:
- Use TestContainers to create ephemeral PostgreSQL and Redis instances
- Each test gets a clean isolated environment
- Containers are automatically created and destroyed
- Require Docker to be running
- Run less frequently, typically in CI/CD pipeline

Example command:
```bash
cd api
python -m pytest tests/integration
```

#### End-to-End Tests

E2E tests verify complete user flows from frontend to backend:
- Test the entire application as a black box
- Require the full application stack to be running
- Run least frequently, typically before releases

Example command:
```bash
cd api
python -m pytest tests/e2e
```

### Frontend Tests

For frontend testing:

```bash
# Navigate to frontend directory
cd frontend

# Run tests
npm test
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- Backend: Follow PEP 8 style guide
- Frontend: Follow ESLint configuration
- Write tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YouTube Data API for providing video data
- OpenAI and Google for AI capabilities
- All open-source libraries used in this project

---

Created by Bruno Santos
