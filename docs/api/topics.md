# Topics API

This document describes the Topics API endpoints for the YouTube Video Summarizer application.

## Topic Endpoints

### GET /api/topics/summary/{summary_id}

Retrieves topics extracted from a specific summary.

#### Path Parameters

- `summary_id` (string, required): The UUID of the summary

#### Query Parameters

- `min_relevance` (float, optional): Minimum relevance score threshold (0.0-1.0, default: 0.5)
- `limit` (integer, optional): Maximum number of topics to return (default: 10, max: 50)

#### Response

```json
{
  "topics": [
    {
      "id": "0a1b2c3d-4e5f-6789-0a1b-2c3d4e5f6789",
      "name": "Machine Learning",
      "relevance": 0.95,
      "description": "The study of computer algorithms that can improve automatically through experience and by the use of data."
    },
    {
      "id": "1b2c3d4e-5f67-890a-1b2c-3d4e5f67890a",
      "name": "Neural Networks",
      "relevance": 0.87,
      "description": "Computing systems vaguely inspired by the biological neural networks that constitute animal brains."
    },
    // Additional topics...
  ],
  "summary": {
    "id": "fedcba98-7654-3210-fedc-ba9876543210",
    "video_id": "123e4567-e89b-12d3-a456-426614174000",
    "model_provider": "openai",
    "date_created": "2023-01-15T15:10:23Z"
  },
  "metadata": {
    "extraction_method": "langchain",
    "model": "openai-gpt4",
    "confidence": 0.88
  }
}
```

#### Status Codes

- 200: Success
- 204: No topics found for this summary
- 404: Summary not found
- 500: Server error

### GET /api/topics/{topic_id}

Retrieves information about a specific topic.

#### Path Parameters

- `topic_id` (string, required): The UUID of the topic

#### Response

```json
{
  "id": "0a1b2c3d-4e5f-6789-0a1b-2c3d4e5f6789",
  "name": "Machine Learning",
  "description": "The study of computer algorithms that can improve automatically through experience and by the use of data.",
  "related_topics": [
    {
      "id": "1b2c3d4e-5f67-890a-1b2c-3d4e5f67890a",
      "name": "Neural Networks",
      "co_occurrence": 0.75
    },
    {
      "id": "2c3d4e5f-6789-0a1b-2c3d-4e5f67890ab",
      "name": "Deep Learning",
      "co_occurrence": 0.68
    },
    // Additional related topics...
  ],
  "summaries_count": 15,
  "videos_count": 12,
  "average_relevance": 0.82
}
```

#### Status Codes

- 200: Success
- 404: Topic not found
- 500: Server error

### POST /api/topics/extract

Manually request topic extraction for a summary.

#### Request Body

```json
{
  "summary_id": "fedcba98-7654-3210-fedc-ba9876543210",
  "model": "gpt-4",
  "min_topics": 3,
  "max_topics": 10,
  "force_refresh": false
}
```

#### Response

```json
{
  "task_id": "b2c3d4e5-f678-90a1-b2c3-d4e5f6789012",
  "status": "PENDING",
  "message": "Topic extraction queued"
}
```

#### Status Codes

- 202: Accepted
- 400: Invalid request parameters
- 404: Summary not found
- 500: Server error

### GET /api/topics/extract/status/{task_id}

Check the status of a topic extraction task.

#### Path Parameters

- `task_id` (string, required): The UUID of the extraction task

#### Response

```json
{
  "task_id": "b2c3d4e5-f678-90a1-b2c3-d4e5f6789012",
  "summary_id": "fedcba98-7654-3210-fedc-ba9876543210",
  "status": "COMPLETED",
  "progress": 100,
  "start_time": "2023-01-15T15:12:34Z",
  "end_time": "2023-01-15T15:13:45Z",
  "topics_count": 8
}
```

#### Status Codes

- 200: Success
- 404: Task not found
- 500: Server error

## Topic Discovery Endpoints

### GET /api/topics/popular

Retrieve the most popular topics across all summaries.

#### Query Parameters

- `user_id` (string, required): The ID of the user
- `limit` (integer, optional): Maximum number of topics to return (default: 20, max: 100)
- `period` (string, optional): Time period for popularity ("day", "week", "month", "year", "all", default: "all")

#### Response

```json
{
  "topics": [
    {
      "id": "0a1b2c3d-4e5f-6789-0a1b-2c3d4e5f6789",
      "name": "Machine Learning",
      "description": "The study of computer algorithms that can improve automatically through experience and by the use of data.",
      "summaries_count": 45,
      "videos_count": 38,
      "channels_count": 12,
      "average_relevance": 0.87
    },
    // Additional topics...
  ]
}
```

#### Status Codes

- 200: Success
- 400: Invalid query parameters
- 401: Unauthorized
- 500: Server error

### GET /api/topics/related/{topic_id}

Find topics that commonly appear together with the specified topic.

#### Path Parameters

- `topic_id` (string, required): The UUID of the topic

#### Query Parameters

- `limit` (integer, optional): Maximum number of related topics to return (default: 10, max: 50)
- `min_co_occurrence` (float, optional): Minimum co-occurrence score (0.0-1.0, default: 0.3)

#### Response

```json
{
  "topic": {
    "id": "0a1b2c3d-4e5f-6789-0a1b-2c3d4e5f6789",
    "name": "Machine Learning",
    "description": "The study of computer algorithms that can improve automatically through experience and by the use of data."
  },
  "related_topics": [
    {
      "id": "1b2c3d4e-5f67-890a-1b2c-3d4e5f67890a",
      "name": "Neural Networks",
      "description": "Computing systems vaguely inspired by the biological neural networks that constitute animal brains.",
      "co_occurrence": 0.75,
      "summaries_count": 32
    },
    // Additional related topics...
  ]
}
```

#### Status Codes

- 200: Success
- 404: Topic not found
- 500: Server error

### GET /api/topics/user/{user_id}

Retrieve topics from a specific user's summaries.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Query Parameters

- `limit` (integer, optional): Maximum number of topics to return (default: 20, max: 100)
- `min_relevance` (float, optional): Minimum relevance score (0.0-1.0, default: 0.5)

#### Response

```json
{
  "topics": [
    {
      "id": "0a1b2c3d-4e5f-6789-0a1b-2c3d4e5f6789",
      "name": "Machine Learning",
      "summaries_count": 12,
      "videos_count": 9,
      "channels": [
        {
          "id": "UC-lHJZR3Gqxm24_Vd_AJ5Yw",
          "title": "Channel Name",
          "videos_count": 5
        },
        // Additional channels...
      ],
      "average_relevance": 0.87
    },
    // Additional topics...
  ],
  "total": 45,
  "limit": 20
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

### GET /api/topics/summaries/{topic_id}

Find summaries that contain a specific topic.

#### Path Parameters

- `topic_id` (string, required): The UUID of the topic

#### Query Parameters

- `user_id` (string, required): The ID of the user
- `limit` (integer, optional): Maximum number of summaries to return (default: 10, max: 50)
- `offset` (integer, optional): Number of summaries to skip (for pagination)
- `min_relevance` (float, optional): Minimum topic relevance in the summary (0.0-1.0, default: 0.5)

#### Response

```json
{
  "topic": {
    "id": "0a1b2c3d-4e5f-6789-0a1b-2c3d4e5f6789",
    "name": "Machine Learning",
    "description": "The study of computer algorithms that can improve automatically through experience and by the use of data."
  },
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
      "topic_relevance": 0.95,
      "date_created": "2023-01-15T15:10:23Z"
    },
    // Additional summaries...
  ],
  "total": 12,
  "limit": 10,
  "offset": 0
}
```

#### Status Codes

- 200: Success
- 404: Topic not found
- 500: Server error

## Implementation Details

The Topics API is implemented with the following components:

- **TopicController**: FastAPI routes for handling topic-related HTTP requests
- **TopicApplicationService**: Application service for orchestrating topic operations
- **TopicRepository**: Data access layer for topic storage and retrieval
- **TopicExtractionService**: Service for extracting topics from summaries
- **LangChainAdapter**: Integration with LangChain for advanced topic extraction

The topic extraction process uses LangChain to:

1. Identify key concepts and topics from the summary content
2. Rank topics by relevance to the main theme of the content
3. Generate brief descriptions for each topic
4. Establish relationships between related topics

Topics are stored in a graph-like structure to enable:
1. Discovery of related topics
2. Building knowledge graphs of video content
3. Recommendation of related videos based on topic similarity

The system uses a hierarchical classification approach to group similar topics and prevent duplication, with regular batch processes to merge semantically identical topics.

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
