# Transcripts API

This document describes the Transcripts API endpoints for the YouTube Video Summarizer application.

## Transcript Endpoints

### GET /api/transcripts/video/{video_id}

Retrieves the transcript for a specific video.

#### Path Parameters

- `video_id` (string, required): The UUID of the video

#### Query Parameters

- `format` (string, optional): Output format (text, json, srt) - Default: text
- `language` (string, optional): Language code for translated transcripts (if available)

#### Response (format=text)

```
00:00:00 Speaker 1: Hello and welcome to this video.
00:00:05 Speaker 1: Today we will be discussing an important topic.
00:00:10 Speaker 2: That's right, and we have a lot to cover.
...
```

#### Response (format=json)

```json
{
  "id": "abcdef12-3456-7890-abcd-123456789abc",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "Hello and welcome to this video.",
      "speaker": "Speaker 1"
    },
    {
      "start": 5.0,
      "end": 10.0,
      "text": "Today we will be discussing an important topic.",
      "speaker": "Speaker 1"
    },
    {
      "start": 10.0,
      "end": 15.0,
      "text": "That's right, and we have a lot to cover.",
      "speaker": "Speaker 2"
    },
    // Additional segments...
  ],
  "metadata": {
    "word_count": 1543,
    "speaker_count": 2,
    "duration": 605.0,
    "source": "youtube_captions",
    "extraction_method": "api"
  },
  "date_created": "2023-01-15T14:27:45Z"
}
```

#### Status Codes

- 200: Success
- 204: No transcript available for this video
- 404: Video not found
- 500: Server error

### POST /api/transcripts/extract

Manually request transcript extraction for a video.

#### Request Body

```json
{
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "force_refresh": false,
  "use_fallback": true
}
```

#### Response

```json
{
  "task_id": "98765432-10fe-dcba-9876-543210fedcba",
  "status": "PENDING",
  "message": "Transcript extraction queued"
}
```

#### Status Codes

- 202: Accepted
- 400: Invalid request parameters
- 404: Video not found
- 500: Server error

### GET /api/transcripts/extract/status/{task_id}

Check the status of a transcript extraction task.

#### Path Parameters

- `task_id` (string, required): The UUID of the extraction task

#### Response

```json
{
  "task_id": "98765432-10fe-dcba-9876-543210fedcba",
  "video_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "COMPLETED",
  "progress": 100,
  "start_time": "2023-01-15T14:25:12Z",
  "end_time": "2023-01-15T14:27:45Z",
  "transcript_id": "abcdef12-3456-7890-abcd-123456789abc"
}
```

#### Status Codes

- 200: Success
- 404: Task not found
- 500: Server error

### POST /api/transcripts/{transcript_id}/translate

Request translation of a transcript to another language.

#### Path Parameters

- `transcript_id` (string, required): The UUID of the transcript to translate

#### Request Body

```json
{
  "target_language": "es",
  "provider": "openai"
}
```

#### Response

```json
{
  "task_id": "abcd1234-56ef-78ab-90cd-ef1234567890",
  "status": "PENDING",
  "message": "Translation task queued"
}
```

#### Status Codes

- 202: Accepted
- 400: Invalid request parameters
- 404: Transcript not found
- 500: Server error

### GET /api/transcripts/search

Search for text within transcripts.

#### Query Parameters

- `user_id` (string, required): The ID of the user
- `query` (string, required): Text to search for
- `limit` (integer, optional): Maximum number of results (default: 10, max: 50)
- `offset` (integer, optional): Number of results to skip (for pagination)

#### Response

```json
{
  "results": [
    {
      "transcript_id": "abcdef12-3456-7890-abcd-123456789abc",
      "video_id": "123e4567-e89b-12d3-a456-426614174000",
      "video_title": "Video Title",
      "channel_title": "Channel Name",
      "matches": [
        {
          "text": "...here is the matching text with the search query highlighted...",
          "start_time": 145.5,
          "end_time": 152.0,
          "confidence": 0.95
        },
        // Additional matches within the same video...
      ]
    },
    // Additional results from other videos...
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

## Transcript Analysis Endpoints

### GET /api/transcripts/{transcript_id}/speakers

Get speaker segmentation information for a transcript.

#### Path Parameters

- `transcript_id` (string, required): The UUID of the transcript

#### Response

```json
{
  "speakers": [
    {
      "id": "speaker_1",
      "label": "Speaker 1",
      "total_segments": 24,
      "total_duration": 320.5,
      "word_count": 850
    },
    {
      "id": "speaker_2",
      "label": "Speaker 2",
      "total_segments": 18,
      "total_duration": 284.5,
      "word_count": 693
    }
  ],
  "metadata": {
    "confidence": 0.85,
    "model": "whisper-speaker-detection-v1"
  }
}
```

#### Status Codes

- 200: Success
- 204: No speaker information available
- 404: Transcript not found
- 500: Server error

### GET /api/transcripts/{transcript_id}/keywords

Get key phrases and terms from a transcript.

#### Path Parameters

- `transcript_id` (string, required): The UUID of the transcript

#### Query Parameters

- `limit` (integer, optional): Maximum number of keywords (default: 20, max: 100)
- `min_relevance` (float, optional): Minimum relevance score (0.0-1.0, default: 0.5)

#### Response

```json
{
  "keywords": [
    {
      "text": "machine learning",
      "relevance": 0.95,
      "count": 12,
      "first_occurrence": 45.2
    },
    {
      "text": "neural networks",
      "relevance": 0.87,
      "count": 8,
      "first_occurrence": 78.5
    },
    // Additional keywords...
  ],
  "metadata": {
    "extraction_method": "ai_keyword_extraction",
    "model": "openai-gpt4"
  }
}
```

#### Status Codes

- 200: Success
- 404: Transcript not found
- 500: Server error

## Implementation Details

The Transcripts API is implemented with the following components:

- **TranscriptController**: FastAPI routes for handling transcript-related HTTP requests
- **TranscriptApplicationService**: Application service for orchestrating transcript operations
- **TranscriptRepository**: Data access layer for transcript storage and retrieval
- **TranscriptExtractor**: Component for extracting transcripts from videos
- **SpeakerSegmentation**: Component for identifying different speakers
- **TranscriptAnalyzer**: Component for analyzing transcript content

The transcript extraction process follows these steps:

1. Try to fetch captions from the YouTube API
2. If captions are not available or are low quality, use Whisper API as a fallback
3. Process the raw transcript data to segment by speaker if possible
4. Store the structured transcript data in the database

For search functionality, the system uses PostgreSQL's full-text search capabilities with custom ranking to provide relevant matches within transcripts.

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
