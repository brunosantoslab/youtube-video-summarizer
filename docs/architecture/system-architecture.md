# YouTube Video Summarizer - System Architecture

## Overview

The YouTube Video Summarizer (YVS) system follows Clean Architecture principles with Domain-Driven Design, using an anemic domain model with service classes. This document outlines the high-level architecture and component interactions.

## Architectural Layers

### 1. Domain Layer

The core of the application, containing:

- **Domain Entities**: Pure data structures representing core business concepts
  - `Video`: Represents a YouTube video with metadata
  - `Summary`: Contains extracted topics and summaries
  - `User`: Represents system user with YouTube authentication
  - `Channel`: Represents a YouTube channel
  - `Topic`: Represents an extracted topic from videos

- **Domain Services**: Contains core business logic
  - `SummaryService`: Business rules for creating and managing summaries
  - `VideoService`: Business rules for video metadata and status management
  - `TopicExtractionService`: Rules for topic identification and relevance

- **Repository Interfaces**: Defines contracts for data access
  - `IVideoRepository`
  - `ISummaryRepository`
  - `IUserRepository`
  - `IChannelRepository`

### 2. Application Layer

Orchestrates the flow of data and coordinates domain operations:

- **Application Services**:
  - `FeedMonitoringService`: Coordinates discovery of new videos
  - `VideoProcessingService`: Manages the video processing workflow
  - `SummaryGenerationService`: Coordinates the summary creation process
  - `UserManagementService`: Handles user-related operations

- **DTOs (Data Transfer Objects)**:
  - Input and output models for application services
  - Validation logic

- **Event Handlers**:
  - `NewVideoDetectedHandler`
  - `ProcessingCompletedHandler`
  - `SummaryGeneratedHandler`

### 3. Infrastructure Layer

Implements technical capabilities and external integrations:

- **Persistence**:
  - `PostgresVideoRepository`: Implements `IVideoRepository`
  - `PostgresSummaryRepository`: Implements `ISummaryRepository`
  - Database migrations and schema management

- **External Services**:
  - `YouTubeApiClient`: Interfaces with YouTube Data API
  - `AIProviderClient`: Interfaces with AI providers (OpenAI, Google)
  - `TranscriptionService`: Handles speech-to-text functionality

- **Message Queue**:
  - `CeleryTaskQueue`: Manages async processing tasks
  - Task definitions and workers

- **Caching**:
  - `RedisCache`: Implements caching for API responses and AI results
  - Cache invalidation strategies

### 4. Presentation Layer

User interfaces and API endpoints:

- **REST API**:
  - `VideoController`: Endpoints for video operations
  - `SummaryController`: Endpoints for summary operations
  - `UserController`: Endpoints for user management
  - API documentation and versioning

- **React Frontend**:
  - Component hierarchy
  - State management
  - Routing

## Cross-Cutting Concerns

- **Authentication**: OAuth2 integration with YouTube
- **Logging**: Structured logging throughout the application
- **Error Handling**: Consistent error handling strategy
- **Configuration**: Environment-based configuration management
- **Monitoring**: Performance and health metrics

## Main Process Flows

### Video Discovery and Processing Flow

1. `FeedMonitoringService` periodically checks for new videos using `YouTubeApiClient`
2. When new videos are found, a `NewVideoDetectedEvent` is published
3. `VideoProcessingService` handles the event and initiates async processing
4. `TranscriptionService` extracts the video transcript
5. `SummaryGenerationService` sends transcript to AI for processing
6. `TopicExtractionService` identifies key topics
7. Results are stored via repositories
8. A `SummaryGeneratedEvent` is published
9. Frontend is updated with new summary data

### User Interaction Flow

1. User authenticates via YouTube OAuth
2. Dashboard displays summarized videos from user's subscriptions
3. User can filter summaries by topic, channel, or date
4. User can select a summary to view detailed topics and insights
5. User can generate notebook links for videos of interest

## Deployment Architecture

- **Application Containers**: Docker containers for backend services
- **Database**: PostgreSQL hosted on Neon
- **Cache**: Redis for transient data
- **Queue**: Redis as message broker for Celery
- **Frontend**: Static assets served via CDN
- **API Gateway**: For routing and request management

## Development and Testing Approach

- **Test-Driven Development**: Comprehensive test coverage
- **Continuous Integration**: Automated testing and deployment
- **Monitoring**: Performance metrics and error tracking
- **Logging**: Structured logs for debugging and analysis

## Future Extensibility

The architecture is designed to allow for future extensions:
- Additional AI providers
- Enhanced topic classification
- User-defined custom summaries
- Content recommendation engine
- Multi-language support

*Author: Bruno Santos*
