# Summaries API

This document describes the Summaries API endpoints for the YouTube Video Summarizer application.

## Summary Endpoints

### GET /api/summaries/video/{video_id}

Retrieves summaries for a specific video.

#### Path Parameters

- `video_id` (string, required): The UUID of the video

#### Query Parameters

- `latest_only` (boolean, optional): Return only the most recent summary (default: true)
- `provider` (string, optional): Filter by AI provider (e.g., "openai", "google")

#### Response

```json
{
  "summaries": [
    {
      "id": "fedcba98-7654-3210-fedc-ba9876543210",
      "video_id": "123e4567-e89b-12d3-a456-426614174000",
      "content": "This is a comprehensive summary of the video content. It covers the main points discussed including the introduction to the topic, key arguments presented by the speakers, supporting evidence, and conclusions drawn.",
      "model_provider": "openai",
      "model_version": "gpt-4",
      "processing_metadata": {
        "processing_time": 3.5,
        "token_count": 2450,
        "prompt_version": "1.5",
        "confidence_score": 0.92,
        "model_parameters": {
          "temperature": 0.7,
          "top_p": 1.0,
          "frequency_penalty": 0.0,
          "presence_penalty": 0.0
        }
      },
      "date_created": "2023-01-15T15:10:23Z"
    },
    // Additional summaries if latest_only=false
  ],
  "video": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "youtube_id": "dQw4w9WgXcQ",
    "title": "Video Title",
    "channel_title": "Channel Name",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
    "duration": "PT10M30S",
    "published_at": "2023-01-01T12:00:00Z"
  }
}
```

#### Status Codes

- 200: Success
- 204: No summaries available for this video
- 404: Video not found
- 500: Server error

### GET /api/summaries/{summary_id}

Retrieves a specific summary by ID.

#### Path Parameters

- `summary_id` (string, required): The UUID of the summary

#### Response

```json
{
  "id": "fedcba98-7654-3210-fedc-ba9876543210",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This is a comprehensive summary of the video content. It covers the main points discussed including the introduction to the topic, key arguments presented by the speakers, supporting evidence, and conclusions drawn.",
  "model_provider": "openai",
  "model_version": "gpt-4",
  "processing_metadata": {
    "processing_time": 3.5,
    "token_count": 2450,
    "prompt_version": "1.5",
    "confidence_score": 0.92,
    "model_parameters": {
      "temperature": 0.7,
      "top_p": 1.0,
      "frequency_penalty": 0.0,
      "presence_penalty": 0.0
    }
  },
  "date_created": "2023-01-15T15:10:23Z",
  "topics": [
    {
      "id": "0a1b2c3d-4e5f-6789-0a1b-2c3d4e5f6789",
      "name": "Machine Learning",
      "relevance": 0.95
    },
    {
      "id": "1b2c3d4e-5f67-890a-1b2c-3d4e5f67890a",
      "name": "Neural Networks",
      "relevance": 0.87
    },
    // Additional topics...
  ],
  "video": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "youtube_id": "dQw4w9WgXcQ",
    "title": "Video Title",
    "channel_title": "Channel Name",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
    "duration": "PT10M30S",
    "published_at": "2023-01-01T12:00:00Z"
  }
}
```

#### Status Codes

- 200: Success
- 404: Summary not found
- 500: Server error

### POST /api/summaries/generate

Manually request summary generation for a video.

#### Request Body

```json
{
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "model_provider": "openai",
  "model_version": "gpt-4",
  "model_parameters": {
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "force_refresh": false
}
```

#### Response

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "status": "PENDING",
  "message": "Summary generation queued"
}
```

#### Status Codes

- 202: Accepted
- 400: Invalid request parameters
- 404: Video not found
- 409: Video has no transcript
- 500: Server error

### GET /api/summaries/generate/status/{task_id}

Check the status of a summary generation task.

#### Path Parameters

- `task_id` (string, required): The UUID of the generation task

#### Response

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "COMPLETED",
  "progress": 100,
  "start_time": "2023-01-15T14:55:23Z",
  "end_time": "2023-01-15T15:10:23Z",
  "summary_id": "fedcba98-7654-3210-fedc-ba9876543210"
}
```

#### Status Codes

- 200: Success
- 404: Task not found
- 500: Server error

### GET /api/summaries/user/{user_id}

Retrieve summaries for a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Query Parameters

- `limit` (integer, optional): Maximum number of summaries to return (default: 20, max: 100)
- `offset` (integer, optional): Number of summaries to skip (for pagination)
- `topic` (string, optional): Filter by topic name
- `provider` (string, optional): Filter by AI provider
- `from_date` (string, optional): Filter by creation date (ISO format)
- `to_date` (string, optional): Filter by creation date (ISO format)

#### Response

```json
{
  "summaries": [
    {
      "id": "fedcba98-7654-3210-fedc-ba9876543210",
      "video": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "youtube_id": "dQw4w9WgXcQ",
        "title": "Video Title",
        "channel_title": "Channel Name",
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
        "published_at": "2023-01-01T12:00:00Z"
      },
      "content_snippet": "This is the beginning of the summary content...",
      "model_provider": "openai",
      "topics": [
        {
          "name": "Machine Learning",
          "relevance": 0.95
        },
        {
          "name": "Neural Networks",
          "relevance": 0.87
        }
      ],
      "date_created": "2023-01-15T15:10:23Z"
    },
    // Additional summaries...
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

## Saved Summaries Endpoints

### GET /api/summaries/saved/user/{user_id}

Retrieve summaries saved by a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Query Parameters

- Same as for `/api/summaries/user/{user_id}`

#### Response

Similar to `/api/summaries/user/{user_id}` but only includes summaries that the user has saved.

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

### POST /api/summaries/saved

Save a summary for a user.

#### Request Body

```json
{
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "summary_id": "fedcba98-7654-3210-fedc-ba9876543210",
  "notes": "Interesting summary about machine learning concepts",
  "tags": ["machine learning", "education", "important"]
}
```

#### Response

```json
{
  "id": "1a2b3c4d-5e6f-7890-1a2b-3c4d5e6f7890",
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "summary_id": "fedcba98-7654-3210-fedc-ba9876543210",
  "notes": "Interesting summary about machine learning concepts",
  "tags": ["machine learning", "education", "important"],
  "date_created": "2023-01-16T09:45:12Z"
}
```

#### Status Codes

- 201: Created
- 400: Invalid request parameters
- 404: User or summary not found
- 409: Summary already saved by user
- 500: Server error

### DELETE /api/summaries/saved/{saved_id}

Remove a saved summary for a user.

#### Path Parameters

- `saved_id` (string, required): The UUID of the saved summary relation

#### Response

```json
{
  "success": true,
  "message": "Saved summary removed successfully"
}
```

#### Status Codes

- 200: Success
- 404: Saved summary not found
- 500: Server error

### PUT /api/summaries/saved/{saved_id}

Update notes or tags for a saved summary.

#### Path Parameters

- `saved_id` (string, required): The UUID of the saved summary relation

#### Request Body

```json
{
  "notes": "Updated notes about this machine learning video",
  "tags": ["machine learning", "education", "important", "review"]
}
```

#### Response

```json
{
  "id": "1a2b3c4d-5e6f-7890-1a2b-3c4d5e6f7890",
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "summary_id": "fedcba98-7654-3210-fedc-ba9876543210",
  "notes": "Updated notes about this machine learning video",
  "tags": ["machine learning", "education", "important", "review"],
  "date_created": "2023-01-16T09:45:12Z",
  "date_modified": "2023-01-16T14:22:45Z"
}
```

#### Status Codes

- 200: Success
- 400: Invalid request parameters
- 404: Saved summary not found
- 500: Server error

## Search Endpoints

### GET /api/summaries/search

Search through all summaries.

#### Query Parameters

- `user_id` (string, required): The ID of the user
- `query` (string, required): Text to search for
- `topics` (array, optional): List of topic names to filter by
- `channels` (array, optional): List of channel IDs to filter by
- `limit` (integer, optional): Maximum number of results (default: 10, max: 50)
- `offset` (integer, optional): Number of results to skip (for pagination)

#### Response

```json
{
  "results": [
    {
      "summary_id": "fedcba98-7654-3210-fedc-ba9876543210",
      "video": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "youtube_id": "dQw4w9WgXcQ",
        "title": "Video Title",
        "channel_title": "Channel Name",
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg"
      },
      "content_snippet": "...text with the search query highlighted...",
      "topics": [
        {
          "name": "Machine Learning",
          "relevance": 0.95
        }
      ],
      "relevance_score": 0.87,
      "date_created": "2023-01-15T15:10:23Z"
    },
    // Additional results...
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

#### Status Codes

- 200: Success
- 400: Invalid query parameters
- 401: Unauthorized
- 500: Server error

## Implementation Details

The Summaries API is implemented with the following components:

- **SummaryController**: FastAPI routes for handling summary-related HTTP requests
- **SummaryApplicationService**: Application service for orchestrating summary operations
- **SummaryRepository**: Data access layer for summary storage and retrieval
- **SummaryGenerationService**: Service for generating summaries from transcripts
- **TopicExtractionService**: Service for extracting topics from summaries
- **AIProviderClient**: Interface for different AI providers (OpenAI, Google)

The summary generation process uses a token optimization strategy to handle long transcripts:

1. For short transcripts (< 4000 tokens), the entire transcript is sent for summarization
2. For medium transcripts (4000-8000 tokens), the transcript is split into sections and summarized individually, then combined
3. For long transcripts (> 8000 tokens), a hierarchical summarization approach is used:
   - First pass: Generate section summaries
   - Second pass: Generate a meta-summary from section summaries

The system includes a fallback strategy between AI providers:

1. Attempt to use the primary provider (typically OpenAI)
2. If an error occurs or rate limits are reached, fall back to the secondary provider (typically Google)
3. If all providers fail, schedule a retry with exponential backoff

All summary results are cached to reduce API costs and improve performance, with configurable TTL based on content type.

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
