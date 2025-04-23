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

## Getting Started

### Prerequisites

- Docker and Docker Compose
- YouTube API credentials
- OpenAI API key (or other supported AI provider)
- Neon PostgreSQL database

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-video-summarizer.git
   cd youtube-video-summarizer
   ```

2. Create a `.env` file with your configuration:
   ```
   # Database
   DATABASE_URL=postgresql://user:password@neon-db-host/yvs
   
   # Redis
   REDIS_URL=redis://redis:6379/0
   
   # YouTube API
   YOUTUBE_API_KEY=your_api_key
   YOUTUBE_CLIENT_ID=your_client_id
   YOUTUBE_CLIENT_SECRET=your_client_secret
   YOUTUBE_REDIRECT_URI=http://localhost:8000/auth/youtube/callback
   
   # AI Providers
   OPENAI_API_KEY=your_openai_key
   GOOGLE_AI_API_KEY=your_google_ai_key
   
   # Application
   SECRET_KEY=your_secret_key
   DEBUG=true
   ENVIRONMENT=development
   ```

3. Start the development environment:
   ```bash
   docker-compose up -d
   ```

4. Run database migrations:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. Access the application:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:3000

### Development Workflow

1. **Backend Development**:
   ```bash
   # Run backend tests
   docker-compose exec api pytest
   
   # Generate migrations
   docker-compose exec api alembic revision --autogenerate -m "Description"
   ```

2. **Frontend Development**:
   ```bash
   # Install dependencies
   cd frontend
   npm install
   
   # Start development server
   npm run dev
   
   # Run tests
   npm test
   ```

## Project Structure

```
.
├── api/                 # Backend API
│   ├── domain/          # Domain layer
│   ├── application/     # Application services
│   ├── infrastructure/  # External integrations
│   └── presentation/    # API controllers
├── frontend/            # React frontend
│   ├── public/          # Static assets
│   └── src/             # Source code
├── tests/               # Test suites
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── docker/              # Docker configuration
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── .github/             # GitHub workflows
├── docker-compose.yml   # Development environment
└── README.md            # This file
```

## Testing

The project includes a comprehensive testing strategy:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user flows
- **Frontend Tests**: Test React components and state

Run the full test suite:
```bash
# Backend tests
docker-compose exec api pytest

# Frontend tests
cd frontend && npm test
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
