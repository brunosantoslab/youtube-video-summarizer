# YouTube Video Summarizer - Component and Flow Diagrams

This document contains key component and flow diagrams that illustrate the architecture and interactions within the YouTube Video Summarizer system.

## System Architecture Components

```mermaid
graph TD
    subgraph Frontend
        A[React UI] --> B[State Management]
        B --> C[API Client]
    end
    
    subgraph Backend
        subgraph Presentation Layer
            D[API Controllers]
            E[DTOs]
            F[Request Validation]
        end
        
        subgraph Application Layer
            G[Application Services]
            H[Event Handlers]
            I[Domain Events]
        end
        
        subgraph Domain Layer
            J[Entities]
            K[Value Objects]
            L[Repository Interfaces]
            M[Domain Services]
        end
        
        subgraph Infrastructure Layer
            N[Repository Implementations]
            O[External API Clients]
            P[Caching Services]
            Q[Queue Services]
            R[Persistence Adapters]
        end
    end
    
    subgraph External Services
        S[YouTube API]
        T[AI Providers]
        U[Database]
        V[Redis Cache/Queue]
    end
    
    C --> D
    D --> G
    G --> J
    G --> M
    G --> I
    H --> I
    G --> L
    L --> N
    N --> R
    R --> U
    O --> S
    O --> T
    P --> V
    Q --> V
```

## Authentication Component Flow

```mermaid
sequenceDiagram
    participant Client as Frontend Client
    participant AC as AuthController
    participant AS as AuthService
    participant YC as YouTubeClient
    participant TR as TokenRepository
    
    Client->>AC: Request Auth URL
    AC->>AS: GetAuthorizationUrl()
    AS->>YC: GenerateAuthUrl()
    YC->>AS: Return Auth URL
    AS->>AC: Return Auth URL
    AC->>Client: Return Auth URL
    
    Client->>AC: Send Auth Code
    AC->>AS: ExchangeCodeForTokens(code)
    AS->>YC: ExchangeCodeForTokens(code)
    YC->>AS: Return Tokens
    AS->>TR: StoreTokens(userId, tokens)
    TR->>AS: Confirm Storage
    AS->>AC: Return Success
    AC->>Client: Return Authentication Result
```

## Video Processing Component Flow

```mermaid
graph TD
    subgraph API Layer
        A[VideoController] --> B[VideoApplicationService]
    end
    
    subgraph Application Services
        B --> C[FeedMonitorService]
        B --> D[VideoProcessingService]
        
        C -- Publishes --> E[VideoDiscoveredEvent]
        D -- Publishes --> F[ProcessingStartedEvent]
        D -- Publishes --> G[ProcessingCompletedEvent]
        D -- Publishes --> H[ProcessingFailedEvent]
    end
    
    subgraph Domain Services
        I[TranscriptExtractionService]
        J[SummaryGenerationService]
        K[TopicExtractionService]
    end
    
    subgraph Infrastructure
        L[YouTubeAPIService]
        M[Celery TaskQueue]
        N[RedisEventPublisher]
        O[PostgresVideoRepository]
    end
    
    subgraph Tasks
        P[extract_transcript_task]
        Q[generate_summary_task]
        R[extract_topics_task]
    end
    
    E --> N
    F --> N
    G --> N
    H --> N
    
    B --> O
    C --> L
    D --> M
    
    M --> P
    P --> I
    I --> L
    
    P --> Q
    Q --> J
    
    Q --> R
    R --> K
```

## AI Processing Component Flow

```mermaid
graph TD
    subgraph AI Processing
        A[SummaryGenerationService] --> B[AIProviderFactory]
        B --> C{Provider Selection}
        C --> D[OpenAIProvider]
        C --> E[GoogleAIProvider]
        
        D --> F[Token Optimizer]
        E --> F
        
        F --> G[Prompt Manager]
        G --> H[Response Processor]
        
        I[TopicExtractionService] --> J[LangChainAdapter]
        J --> K[TopicExtractor]
        K --> L[TopicRanker]
    end
    
    subgraph Caching
        M[AICacheService]
        N[RedisCache]
    end
    
    subgraph Monitoring
        O[AIUsageTracker]
        P[CostOptimizer]
    end
    
    A --> M
    M --> N
    D --> O
    E --> O
    O --> P
    P --> F
```

## Data Flow - Video to Summary

```mermaid
flowchart TD
    A[YouTube Video] -->|API Client| B[Video Metadata]
    B -->|Process| C[Video Entity]
    
    A -->|Captions API| D[Raw Captions]
    D -->|Extract| E[Transcript Entity]
    
    E -->|AI Processing| F[Summary Entity]
    F -->|Topic Extraction| G[Topic Entities]
    
    C -->|Store| H[(Database)]
    E -->|Store| H
    F -->|Store| H
    G -->|Store| H
    
    I[User Request] -->|API| J[Summary View]
    J -->|Fetch| H
    J -->|Render| K[UI Display]
```

## Caching and Optimization Flow

```mermaid
flowchart TD
    A[API Request] -->|Check Cache| B{Cache Hit?}
    
    B -->|Yes| C[Return Cached Result]
    B -->|No| D[Process Request]
    
    D -->|External API Call| E[YouTube API]
    D -->|AI Processing| F[AI Provider]
    
    E -->|Result| G[Cache Result]
    F -->|Result| G
    
    G -->|Token Tracking| H[Usage Monitor]
    G -->|Expiration| I[TTL Manager]
    
    G --> J[Return Fresh Result]
    
    H -->|Budget Analysis| K[Cost Optimizer]
    K -->|Strategy Selection| L[Provider Selector]
```

## Event-Driven Communication Flow

```mermaid
graph TD
    subgraph Publishers
        A[VideoService]
        B[TranscriptService]
        C[SummaryService]
    end
    
    subgraph EventBus
        D[Redis Pub/Sub]
    end
    
    subgraph Subscribers
        E[ProcessingTaskService]
        F[NotificationService]
        G[AnalyticsService]
    end
    
    subgraph Events
        H[VideoDiscoveredEvent]
        I[TranscriptExtractedEvent]
        J[SummaryGeneratedEvent]
        K[ProcessingFailedEvent]
    end
    
    A -- Publishes --> H
    B -- Publishes --> I
    C -- Publishes --> J
    A -- Publishes --> K
    
    H --> D
    I --> D
    J --> D
    K --> D
    
    D -- Subscribes --> E
    D -- Subscribes --> F
    D -- Subscribes --> G
```

## User Interaction Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as React UI
    participant API as Backend API
    participant YT as YouTube API
    participant AI as AI Service
    participant DB as Database
    
    User->>UI: Login with YouTube
    UI->>API: Authentication Request
    API->>YT: OAuth Flow
    YT->>API: Authentication Response
    API->>DB: Store User & Tokens
    API->>UI: Auth Success
    UI->>User: Show Dashboard
    
    User->>UI: Add Video
    UI->>API: Create Video Request
    API->>YT: Fetch Video Metadata
    YT->>API: Video Metadata
    API->>DB: Store Video Entity
    API->>UI: Processing Started
    
    note over API: Async Processing
    API->>YT: Request Captions
    YT->>API: Captions Data
    API->>DB: Store Transcript
    API->>AI: Generate Summary
    AI->>API: Summary Content
    API->>DB: Store Summary
    API->>AI: Extract Topics
    AI->>API: Topic List
    API->>DB: Store Topics
    
    User->>UI: View Summary
    UI->>API: Request Summary
    API->>DB: Fetch Summary & Topics
    DB->>API: Return Data
    API->>UI: Summary Data
    UI->>User: Display Summary
```

## Repository Pattern Implementation

```mermaid
graph TD
    subgraph Domain Layer
        A[Domain Entity]
        B[Repository Interface]
    end
    
    subgraph Infrastructure Layer
        C[Repository Implementation]
        D[ORM Entity]
        E[Mappers]
    end
    
    subgraph Data Access
        F[Database Session]
        G[Query Builder]
    end
    
    A -.-> B
    B <|.. C
    C --> D
    C --> E
    E --> A
    E --> D
    C --> F
    C --> G
```

## Error Handling Flow

```mermaid
flowchart TD
    A[API Request] --> B{Process Request}
    
    B -->|Success| C[Return Response]
    B -->|Error| D{Error Type}
    
    D -->|Validation Error| E[Return 400]
    D -->|Not Found| F[Return 404]
    D -->|Unauthorized| G[Return 401]
    D -->|External API Error| H{Retry?}
    D -->|Internal Error| I[Log Error]
    
    H -->|Yes| J[Retry Strategy]
    H -->|No| K[Return 503]
    
    J -->|Success| C
    J -->|Max Retries| K
    
    I --> L[Return 500]
    
    E --> M[Log Validation Failure]
    F --> N[Log Not Found]
    G --> O[Log Auth Failure]
```

## Testing Architecture

```mermaid
graph TD
    subgraph Unit Tests
        A[Domain Model Tests]
        B[Service Tests]
        C[Repository Tests]
    end
    
    subgraph Integration Tests
        D[Repository Integration]
        E[Service Integration]
        F[API Endpoint Tests]
    end
    
    subgraph Test Infrastructure
        G[TestContainers]
        H[Postgres Container]
        I[Redis Container]
        J[Mock YouTube API]
        K[Mock AI Providers]
    end
    
    subgraph CI/CD Pipeline
        L[Run Unit Tests]
        M[Run Integration Tests]
        N[Code Coverage]
        O[Quality Gates]
    end
    
    D --> G
    E --> G
    F --> G
    
    G --> H
    G --> I
    E --> J
    E --> K
    
    L --> A
    L --> B
    L --> C
    
    M --> D
    M --> E
    M --> F
    
    L --> N
    M --> N
    N --> O
```

## Frontend Component Architecture

```mermaid
graph TD
    subgraph Components
        A[App]
        B[Layout]
        C[AuthProvider]
        D[Router]
        
        E[Dashboard]
        F[VideoExplorer]
        G[SummaryViewer]
        H[TopicExplorer]
        I[SearchResults]
        J[UserSettings]
        
        K[VideoCard]
        L[SummaryCard]
        M[TopicTag]
        N[SearchBar]
        O[Pagination]
        P[LoadingIndicator]
    end
    
    subgraph State Management
        Q[Redux Store]
        R[Auth Slice]
        S[Videos Slice]
        T[Summaries Slice]
        U[Topics Slice]
        V[UI Slice]
    end
    
    subgraph API Integration
        W[API Client]
        X[Auth API]
        Y[Videos API]
        Z[Summaries API]
        AA[Topics API]
        AB[Users API]
    end
    
    A --> B
    A --> C
    A --> D
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J
    
    E --> K
    E --> L
    E --> M
    E --> N
    
    F --> K
    F --> O
    F --> P
    
    G --> L
    G --> M
    
    H --> M
    H --> L
    
    I --> K
    I --> L
    I --> O
    
    C --> R
    E --> S
    E --> T
    E --> U
    
    R --> X
    S --> Y
    T --> Z
    U --> AA
    J --> AB
```

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
