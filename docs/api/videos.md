# Videos API

This document describes the Videos API endpoints for the YouTube Video Summarizer application.

## Videos Endpoints

### GET /api/videos

Retrieves a list of videos, with optional filtering parameters.

#### Query Parameters

- `user_id` (string, required): The ID of the user for whom to fetch videos
- `status` (string, optional): Filter by video status (NEW, PROCESSING, PROCESSED, FAILED)
- `channel_id` (string, optional): Filter by YouTube channel ID
- `from_date` (string, optional): Filter by publish date (ISO format)
- `to_date` (string, optional): Filter by publish date (ISO format)
- `limit` (integer, optional): Maximum number of videos to return (default: 20, max: 100)
- `offset` (integer, optional): Number of videos to skip (for pagination)

#### Response

```json
{
  "videos": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "youtube_id": "dQw4w9WgXcQ",
      "title": "Video Title",
      "description": "Video description text here...",
      "channel_id": "UC-lHJZR3Gqxm24_Vd_AJ5Yw",
      "channel_title": "Channel Name",
      "published_at": "2023-01-01T12:00:00Z",
      "duration": "PT10M30S",
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
      "status": "PROCESSED",
      "date_created": "2023-01-15T14:23:45Z",
      "date_modified": "2023-01-15T15:30:12Z"
    },
    // Additional videos...
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

#### Status Codes

- 200: Success
- 400: Invalid query parameters
- 401: Unauthorized
- 500: Server error

### GET /api/videos/{video_id}

Retrieves detailed information about a specific video.

#### Path Parameters

- `video_id` (string, required): The UUID of the video to retrieve

#### Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "youtube_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "description": "Video description text here...",
  "channel_id": "UC-lHJZR3Gqxm24_Vd_AJ5Yw",
  "channel_title": "Channel Name",
  "published_at": "2023-01-01T12:00:00Z",
  "duration": "PT10M30S",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
  "status": "PROCESSED",
  "date_created": "2023-01-15T14:23:45Z",
  "date_modified": "2023-01-15T15:30:12Z",
  "transcript": {
    "id": "abcdef12-3456-7890-abcd-123456789abc",
    "language": "en",
    "word_count": 1543
  },
  "summaries": [
    {
      "id": "fedcba98-7654-3210-fedc-ba9876543210",
      "model_provider": "openai",
      "model_version": "gpt-4",
      "date_created": "2023-01-15T15:10:23Z"
    }
  ]
}
```

#### Status Codes

- 200: Success
- 404: Video not found
- 500: Server error

### POST /api/videos

Adds a new video to process from a YouTube URL.

#### Request Body

```json
{
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

#### Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "youtube_id": "dQw4w9WgXcQ",
  "status": "NEW",
  "date_created": "2023-01-15T14:23:45Z"
}
```

#### Status Codes

- 201: Created
- 400: Invalid request parameters
- 401: Unauthorized
- 409: Video already exists
- 500: Server error

### GET /api/videos/status/{video_id}

Gets the processing status of a video.

#### Path Parameters

- `video_id` (string, required): The UUID of the video

#### Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "PROCESSING",
  "progress": 65,
  "tasks": {
    "transcript_extraction": {
      "status": "COMPLETED",
      "progress": 100,
      "started_at": "2023-01-15T14:25:12Z",
      "completed_at": "2023-01-15T14:27:45Z"
    },
    "summary_generation": {
      "status": "PROCESSING",
      "progress": 60,
      "started_at": "2023-01-15T14:28:02Z",
      "completed_at": null
    },
    "topic_extraction": {
      "status": "PENDING",
      "progress": 0,
      "started_at": null,
      "completed_at": null
    }
  },
  "error": null
}
```

#### Status Codes

- 200: Success
- 404: Video not found
- 500: Server error

### POST /api/videos/refresh/{video_id}

Manually retries processing for a failed video.

#### Path Parameters

- `video_id` (string, required): The UUID of the video to retry

#### Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "PROCESSING",
  "message": "Video processing restarted successfully"
}
```

#### Status Codes

- 202: Accepted
- 404: Video not found
- 409: Video is not in a failed state
- 500: Server error

### DELETE /api/videos/{video_id}

Deletes a video and all its associated data.

#### Path Parameters

- `video_id` (string, required): The UUID of the video to delete

#### Response

```json
{
  "success": true,
  "message": "Video and all associated data deleted successfully"
}
```

#### Status Codes

- 200: Success
- 404: Video not found
- 500: Server error

## Video Discovery Endpoints

### GET /api/videos/subscriptions/{user_id}

Gets videos from the user's YouTube subscriptions.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Query Parameters

- `limit` (integer, optional): Maximum number of videos to return (default: 20, max: 50)
- `from_date` (string, optional): Filter by publish date (ISO format)

#### Response

```json
{
  "videos": [
    {
      "youtube_id": "dQw4w9WgXcQ",
      "title": "Video Title",
      "channel_title": "Channel Name",
      "published_at": "2023-01-01T12:00:00Z",
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
      "duration": "PT10M30S",
      "is_processed": false
    },
    // Additional videos...
  ]
}
```

#### Status Codes

- 200: Success
- 401: Unauthorized (YouTube auth required)
- 404: User not found
- 500: Server error

### POST /api/videos/import-batch

Imports a batch of videos for processing.

#### Request Body

```json
{
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "videos": [
    {
      "youtube_id": "dQw4w9WgXcQ",
      "title": "Optional video title (will be fetched if not provided)"
    },
    {
      "youtube_id": "9bZkp7q19f0"
    },
    // Additional videos...
  ]
}
```

#### Response

```json
{
  "success": true,
  "processed": 3,
  "failed": 0,
  "video_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "234f5678-f90a-12b3-c456-726614174001",
    "345g6789-0a1b-23c4-d567-8266141740e2"
  ]
}
```

#### Status Codes

- 202: Accepted
- 400: Invalid request body
- 401: Unauthorized
- 500: Server error

## Implementation Details

The Videos API is implemented with the following components:

- **VideoController**: FastAPI routes for handling video-related HTTP requests
- **VideoApplicationService**: Application service for orchestrating video operations
- **VideoRepository**: Data access layer for video storage and retrieval
- **YouTubeApiService**: Service for interacting with the YouTube API
- **ProcessingTaskService**: Service for managing asynchronous processing tasks

Events are emitted during video processing to enable asynchronous pipeline execution:

1. `VideoDiscoveredEvent`: Triggered when a new video is discovered
2. `ProcessingStartedEvent`: Triggered when video processing begins
3. `ProcessingCompletedEvent`: Triggered when processing finishes successfully
4. `ProcessingFailedEvent`: Triggered when processing fails

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
