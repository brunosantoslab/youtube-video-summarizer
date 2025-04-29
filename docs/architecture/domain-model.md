# YouTube Video Summarizer - Domain Model

This document defines the core domain entities, value objects, and their relationships for the YouTube Video Summarizer application.

## Domain Entities

### User
Represents a user of the application.

**Properties:**
- `Id`: UUID
- `Email`: String
- `YouTubeUserId`: String
- `DisplayName`: String
- `PreferenceSettings`: UserPreferences
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Has many Subscriptions
- Has many SavedSummaries

### Video
Represents a YouTube video.

**Properties:**
- `Id`: UUID
- `YouTubeId`: String
- `Title`: String
- `Description`: String
- `ChannelId`: String
- `ChannelTitle`: String
- `PublishedAt`: DateTime
- `Duration`: TimeSpan
- `ThumbnailUrl`: String
- `Status`: VideoStatus (Enum: New, Processing, Processed, Failed)
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Belongs to Channel
- Has one Transcript
- Has one Summary
- Has many Topics

### Channel
Represents a YouTube channel.

**Properties:**
- `Id`: UUID
- `YouTubeId`: String
- `Title`: String
- `Description`: String
- `ThumbnailUrl`: String
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Has many Videos
- Has many Subscriptions

### Subscription
Represents a user's subscription to a channel.

**Properties:**
- `Id`: UUID
- `UserId`: UUID
- `ChannelId`: UUID
- `DateSubscribed`: DateTime
- `NotificationsEnabled`: Boolean
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Belongs to User
- Belongs to Channel

### Transcript
Represents the textual content of a video.

**Properties:**
- `Id`: UUID
- `VideoId`: UUID
- `Content`: Text
- `SourceType`: TranscriptSourceType (Enum: YouTube, Whisper, Manual)
- `LanguageCode`: String
- `ProcessingStatus`: ProcessingStatus
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Belongs to Video

### Summary
Represents an AI-generated summary of a video.

**Properties:**
- `Id`: UUID
- `VideoId`: UUID
- `Content`: Text
- `ModelProvider`: String
- `ModelVersion`: String
- `ProcessingMetadata`: SummaryMetadata
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Belongs to Video
- Has many Topics

### Topic
Represents a key topic extracted from a video.

**Properties:**
- `Id`: UUID
- `VideoId`: UUID
- `SummaryId`: UUID
- `Name`: String
- `Description`: String
- `Relevance`: Float (0-1)
- `StartTime`: TimeSpan (optional)
- `EndTime`: TimeSpan (optional)
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Belongs to Video
- Belongs to Summary
- May relate to other Topics

### SavedSummary
Represents a summary saved by a user for later reference.

**Properties:**
- `Id`: UUID
- `UserId`: UUID
- `SummaryId`: UUID
- `Notes`: Text
- `FolderName`: String
- `DateSaved`: DateTime
- `DateCreated`: DateTime
- `DateModified`: DateTime

**Relationships:**
- Belongs to User
- References Summary

## Value Objects

### UserPreferences
Contains user preference settings.

**Properties:**
- `SummaryLength`: Enum (Brief, Standard, Detailed)
- `TopicHighlightCount`: Integer
- `DefaultLanguage`: String
- `EmailNotifications`: Boolean
- `NotebookIntegrationEnabled`: Boolean

### ProcessingStatus
Tracks the status of processing operations.

**Properties:**
- `Status`: Enum (Pending, InProgress, Completed, Failed)
- `ErrorMessage`: String (optional)
- `CompletionPercentage`: Float (0-100)
- `LastProcessed`: DateTime

### SummaryMetadata
Contains metadata about the summary generation process.

**Properties:**
- `ProcessingTime`: TimeSpan
- `TokenCount`: Integer
- `PromptVersion`: String
- `ConfidenceScore`: Float (0-1)
- `ModelParameters`: Dictionary<String, Object>

## Domain Events

### VideoDiscoveredEvent
Triggered when a new video is found in a user's feed.

### ProcessingStartedEvent
Triggered when video processing begins.

### TranscriptExtractedEvent
Triggered when a transcript has been successfully extracted.

### SummaryGeneratedEvent
Triggered when an AI summary has been created.

### TopicsExtractedEvent
Triggered when topics have been identified from a video.

## Domain Services

### IVideoService
Manages operations related to videos.

**Methods:**
- `DiscoverNewVideos(userId)`
- `UpdateVideoStatus(videoId, status)`
- `GetVideoById(videoId)`
- `GetVideosByChannel(channelId)`

### ISummaryService
Manages operations related to summaries.

**Methods:**
- `GenerateSummary(videoId)`
- `GetSummaryByVideo(videoId)`
- `SaveSummaryForUser(userId, summaryId)`
- `GetSavedSummariesByUser(userId)`

### ITopicExtractionService
Manages operations related to topic extraction.

**Methods:**
- `ExtractTopics(summaryId)`
- `GetTopicsByVideo(videoId)`
- `GetTopicsBySummary(summaryId)`
- `RankTopicsByRelevance(videoId)`

### ITranscriptionService
Manages operations related to video transcription.

**Methods:**
- `ExtractTranscript(videoId)`
- `GetTranscriptByVideo(videoId)`
- `UpdateTranscript(transcriptId, content)`

## Repository Interfaces

### IUserRepository
- `GetById(id)`
- `GetByYouTubeId(youtubeId)`
- `Create(user)`
- `Update(user)`
- `Delete(id)`

### IVideoRepository
- `GetById(id)`
- `GetByYouTubeId(youtubeId)`
- `GetByStatus(status)`
- `GetByChannel(channelId)`
- `Create(video)`
- `Update(video)`
- `Delete(id)`

### IChannelRepository
- `GetById(id)`
- `GetByYouTubeId(youtubeId)`
- `GetBySubscription(userId)`
- `Create(channel)`
- `Update(channel)`
- `Delete(id)`

### ISummaryRepository
- `GetById(id)`
- `GetByVideo(videoId)`
- `GetSavedByUser(userId)`
- `Create(summary)`
- `Update(summary)`
- `Delete(id)`

### ITopicRepository
- `GetById(id)`
- `GetByVideo(videoId)`
- `GetBySummary(summaryId)`
- `Create(topic)`
- `Update(topic)`
- `Delete(id)`

*Author: Bruno Santos*
