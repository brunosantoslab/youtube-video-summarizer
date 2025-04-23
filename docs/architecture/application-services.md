# YouTube Video Summarizer - Application Services

This document outlines the key application services that orchestrate the business logic of the YouTube Video Summarizer. These services coordinate between the domain layer and infrastructure components.

## Core Application Services

### FeedMonitoringService

Responsible for discovering new videos from user subscriptions.

**Dependencies:**
- `IUserRepository`
- `IChannelRepository`
- `IVideoRepository`
- `YouTubeApiClient`
- `EventPublisher`

**Key Methods:**
- `CheckForNewVideos(userId)`: Queries YouTube API for new videos in user's subscriptions
- `SchedulePeriodicChecks()`: Sets up periodic job to check for new content
- `ProcessNewVideo(videoData)`: Creates new Video entity and publishes discovery event
- `GetLatestVideosForUser(userId)`: Returns recent videos from user's subscriptions

**Events Published:**
- `VideoDiscoveredEvent`

### VideoProcessingService

Orchestrates the video processing workflow.

**Dependencies:**
- `IVideoRepository`
- `ITranscriptionService`
- `EventPublisher`
- `TaskQueueService`

**Key Methods:**
- `QueueVideoForProcessing(videoId)`: Adds video to processing queue
- `ProcessVideo(videoId)`: Coordinates the processing workflow
- `UpdateVideoStatus(videoId, status)`: Updates processing status
- `GetProcessingStatus(videoId)`: Returns current processing state
- `HandleProcessingFailure(videoId, error)`: Manages error recovery

**Events Published:**
- `ProcessingStartedEvent`
- `ProcessingCompletedEvent`
- `ProcessingFailedEvent`

### TranscriptionService

Manages the extraction and processing of video transcripts.

**Dependencies:**
- `IVideoRepository`
- `ITranscriptRepository`
- `YouTubeApiClient`
- `WhisperApiClient`
- `EventPublisher`

**Key Methods:**
- `ExtractTranscript(videoId)`: Gets transcript from YouTube or generates via Whisper
- `ProcessTranscript(transcriptId)`: Cleans and prepares transcript for analysis
- `DetectLanguage(transcriptId)`: Identifies transcript language
- `GetTranscriptByVideo(videoId)`: Retrieves processed transcript

**Events Published:**
- `TranscriptExtractedEvent`
- `TranscriptProcessedEvent`

### SummaryGenerationService

Coordinates the generation of video summaries using AI.

**Dependencies:**
- `IVideoRepository`
- `ITranscriptRepository`
- `ISummaryRepository`
- `AIProviderClient`
- `EventPublisher`

**Key Methods:**
- `GenerateSummary(videoId)`: Creates summary from transcript using AI
- `OptimizePrompt(transcript)`: Prepares transcript for AI processing
- `SaveSummary(videoId, summaryContent)`: Persists generated summary
- `RegenerateSummary(summaryId)`: Recreates summary with different parameters

**Events Published:**
- `SummaryGeneratedEvent`
- `SummaryRegeneratedEvent`

### TopicExtractionService

Manages the identification and analysis of key topics within videos.

**Dependencies:**
- `IVideoRepository`
- `ISummaryRepository`
- `ITopicRepository`
- `AIProviderClient`
- `LangChainService`
- `EventPublisher`

**Key Methods:**
- `ExtractTopics(summaryId)`: Identifies key topics from summary
- `RankTopicsByRelevance(videoId)`: Prioritizes topics by importance
- `LinkRelatedTopics(topicId)`: Finds connections between topics
- `DetectTopicTimestamps(videoId, topicId)`: Attempts to identify when topics appear in video

**Events Published:**
- `TopicsExtractedEvent`
- `TopicsRankedEvent`

### UserManagementService

Handles user-related operations and preferences.

**Dependencies:**
- `IUserRepository`
- `ISubscriptionRepository`
- `YouTubeApiClient`
- `AuthenticationService`

**Key Methods:**
- `RegisterUser(userData)`: Creates new user from YouTube auth
- `UpdateUserPreferences(userId, preferences)`: Modifies user settings
- `SyncYouTubeSubscriptions(userId)`: Updates subscriptions from YouTube
- `GetUserProfile(userId)`: Retrieves user information and preferences

### NotebookIntegrationService

Manages integration with notebook environments.

**Dependencies:**
- `IVideoRepository`
- `ISummaryRepository`
- `ITopicRepository`
- `NotebookLinkGenerator`

**Key Methods:**
- `GenerateNotebookLink(videoId)`: Creates link for notebook viewing
- `FormatSummaryForNotebook(summaryId)`: Prepares summary for notebook display
- `GenerateEmbedCode(videoId)`: Creates embed code for video
- `CreateInteractiveNotebook(videoId)`: Generates interactive notebook with video and summary

## Application DTOs

### VideoDiscoveryDTO

Data transfer object for new video information.

**Properties:**
- `YouTubeId`: String
- `Title`: String
- `Description`: String
- `ChannelId`: String
- `ChannelTitle`: String
- `PublishedAt`: DateTime
- `ThumbnailUrl`: String

### SummaryGenerationRequestDTO

Data transfer object for summary generation requests.

**Properties:**
- `VideoId`: UUID
- `PreferredLength`: Enum (Brief, Standard, Detailed)
- `HighlightTopicsCount`: Integer
- `LanguageCode`: String
- `ModelPreference`: String (optional)

### TopicExtractionRequestDTO

Data transfer object for topic extraction requests.

**Properties:**
- `SummaryId`: UUID
- `MinRelevanceScore`: Float
- `MaxTopicsCount`: Integer
- `IncludeTimestamps`: Boolean

### UserPreferencesDTO

Data transfer object for user preferences.

**Properties:**
- `SummaryLength`: Enum (Brief, Standard, Detailed)
- `TopicHighlightCount`: Integer
- `DefaultLanguage`: String
- `EmailNotifications`: Boolean
- `NotebookIntegrationEnabled`: Boolean

## Event Handlers

### NewVideoDetectedHandler

Handles the processing of newly discovered videos.

**Events Handled:**
- `VideoDiscoveredEvent`

**Actions:**
- Updates video database entry
- Triggers video processing workflow
- Updates user feed

### TranscriptExtractedHandler

Processes completed transcript extractions.

**Events Handled:**
- `TranscriptExtractedEvent`

**Actions:**
- Updates transcript status
- Triggers summary generation
- Logs completion metrics

### SummaryGeneratedHandler

Handles newly generated summaries.

**Events Handled:**
- `SummaryGeneratedEvent`

**Actions:**
- Updates summary database entry
- Triggers topic extraction
- Notifies user if configured
- Updates dashboard

### ProcessingFailureHandler

Manages recovery from processing failures.

**Events Handled:**
- `ProcessingFailedEvent`

**Actions:**
- Logs failure details
- Attempts recovery strategies
- Updates status for user visibility
- Schedules retry if appropriate

## Application Services Interfaces

### IFeedMonitoringService
```csharp
public interface IFeedMonitoringService
{
    Task CheckForNewVideos(Guid userId);
    Task SchedulePeriodicChecks();
    Task ProcessNewVideo(VideoDiscoveryDTO videoData);
    Task<IEnumerable<VideoDTO>> GetLatestVideosForUser(Guid userId, int limit = 20);
}
```

### IVideoProcessingService
```csharp
public interface IVideoProcessingService
{
    Task QueueVideoForProcessing(Guid videoId);
    Task ProcessVideo(Guid videoId);
    Task UpdateVideoStatus(Guid videoId, VideoStatus status);
    Task<ProcessingStatus> GetProcessingStatus(Guid videoId);
    Task HandleProcessingFailure(Guid videoId, string error);
}
```

### ISummaryGenerationService
```csharp
public interface ISummaryGenerationService
{
    Task<Guid> GenerateSummary(Guid videoId);
    Task<string> OptimizePrompt(string transcript);
    Task<Guid> SaveSummary(Guid videoId, string summaryContent);
    Task<Guid> RegenerateSummary(Guid summaryId, SummaryGenerationRequestDTO request);
}
```

### ITopicExtractionService
```csharp
public interface ITopicExtractionService
{
    Task<IEnumerable<Guid>> ExtractTopics(Guid summaryId);
    Task<IEnumerable<TopicDTO>> RankTopicsByRelevance(Guid videoId);
    Task LinkRelatedTopics(Guid topicId);
    Task<IDictionary<Guid, TimeRange>> DetectTopicTimestamps(Guid videoId, IEnumerable<Guid> topicIds);
}
```

*Author: Bruno Santos*
