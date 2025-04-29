# YouTube Video Summarizer - API Routes

This document provides a comprehensive reference of all API endpoints implemented in the YouTube Video Summarizer application.

## Authentication API

### YouTube Authentication

Base path: `/api/auth/youtube`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| GET | `/auth-url` | Get YouTube authentication URL | `user_id` (query), `redirect_path` (query, optional) | `auth_url`: URL for YouTube OAuth |
| GET | `/callback` | Handle YouTube OAuth callback | `code` (query), `state` (query) | Redirect or error response |
| GET | `/status` | Check if a user is authenticated | `user_id` (query) | `authenticated`: boolean, `scopes`: array of scope strings |
| POST | `/revoke` | Revoke YouTube access | `user_id` in request body | 204 No Content |

#### Authentication Flow

1. Client requests an authentication URL with the user ID
2. Client redirects the user to the returned URL
3. User authenticates with YouTube and grants permissions
4. YouTube redirects back to the callback URL with an authorization code
5. The application exchanges the code for access/refresh tokens
6. Client can check authentication status and revoke access if needed

## YouTube Feed API

Base path: `/api/youtube/feed`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| GET | `/subscriptions` | Get user's YouTube subscriptions | `user_id` (query) | Array of subscription objects |
| GET | `/recent-videos` | Get recent videos from subscriptions | `user_id` (query), `max_days` (query, default: 7), `max_videos` (query, default: 20) | Array of video objects |
| GET | `/video/{video_id}` | Get details for specific video | `video_id` (path), `user_id` (query), `with_transcript` (query, default: false), `language_code` (query, default: "en") | Video details object |
| GET | `/monitor/{user_id}` | Check for new videos in feed | `user_id` (path) | Feed check status object |

### Subscription Object

```json
{
  "channel_id": "string",
  "title": "string",
  "description": "string",
  "thumbnail_url": "string"
}
```

### Video Object

```json
{
  "video_id": "string",
  "title": "string",
  "description": "string",
  "channel_id": "string",
  "channel_title": "string",
  "published_at": "string",
  "thumbnail_url": "string"
}
```

### Feed Check Response

```json
{
  "success": true,
  "user_id": "string",
  "new_videos_count": 0,
  "monitored_at": "string",
  "error": "string"
}
```

## AI Optimization API

Base path: `/api/ai-optimization`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| GET | `/cache-stats` | Get AI cache statistics | None | Cache statistics object |
| GET | `/budget-info` | Get AI budget information | None | Budget information object |
| GET | `/usage-history` | Get AI usage history | `days` (query, default: 7) | Usage history object |
| POST | `/clear-cache` | Clear AI cache | `cache_type` (body, optional) | Clear cache response |

### Cache Statistics Object

```json
{
  "enabled": true,
  "entries": 0,
  "ttl": 3600,
  "types": {
    "summary": 0,
    "topic": 0,
    "transcript": 0
  }
}
```

### Budget Information Object

```json
{
  "date": "string",
  "daily_budget": 0.0,
  "current_cost": 0.0,
  "remaining_budget": 0.0,
  "percentage_used": 0.0,
  "is_budget_exceeded": false,
  "providers": {
    "openai": {
      "calls": 0,
      "cost": 0.0
    },
    "google": {
      "calls": 0,
      "cost": 0.0
    }
  }
}
```

### Usage History Object

```json
{
  "history": {
    "2025-04-29": {
      "total_cost": 0.0,
      "openai": {
        "calls": 0,
        "cost": 0.0
      },
      "google": {
        "calls": 0,
        "cost": 0.0
      }
    }
  },
  "total_cost": 0.0,
  "days": 7
}
```

### Clear Cache Request/Response

Request:
```json
{
  "cache_type": "summary" // optional, can be "summary", "topic", "transcript", or null for all
}
```

Response:
```json
{
  "cleared": 5,
  "message": "Successfully cleared 5 entries from summary cache"
}
```

## Video Processing API

Note: The Video Processing API endpoints need to be implemented. Based on the domain model and services, the following endpoints are planned:

Base path: `/api/videos`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| POST | `/` | Add video for processing | `youtube_id` (body), `user_id` (body) | Video object with processing status |
| GET | `/{video_id}` | Get video details | `video_id` (path) | Video details with processing status |
| GET | `/{video_id}/status` | Get processing status | `video_id` (path) | Processing status object |
| GET | `/user/{user_id}` | List videos for user | `user_id` (path), `status` (query, optional), `page` (query, optional), `limit` (query, optional) | Paginated list of videos |

## Transcript API

Note: The Transcript API endpoints need to be implemented. Based on the domain model and services, the following endpoints are planned:

Base path: `/api/transcripts`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| GET | `/{video_id}` | Get transcript for video | `video_id` (path), `format` (query, optional) | Transcript object |
| POST | `/{video_id}` | Create/update transcript | `video_id` (path), `content` (body), `language` (body) | Created/updated transcript |

## Summary API

Note: The Summary API endpoints need to be implemented. Based on the domain model and services, the following endpoints are planned:

Base path: `/api/summaries`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| GET | `/{video_id}` | Get summary for video | `video_id` (path) | Summary object |
| POST | `/{video_id}` | Generate/regenerate summary | `video_id` (path), `options` (body, optional) | Processing status |
| POST | `/{video_id}/save` | Save summary for user | `video_id` (path), `user_id` (body), `notes` (body, optional) | Saved summary object |
| GET | `/user/{user_id}` | List summaries for user | `user_id` (path), `page` (query, optional), `limit` (query, optional) | Paginated list of summaries |

## Topics API

Note: The Topics API endpoints need to be implemented. Based on the domain model and services, the following endpoints are planned:

Base path: `/api/topics`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| GET | `/{video_id}` | Get topics for video | `video_id` (path) | List of topics |
| GET | `/trending` | Get trending topics | `limit` (query, optional), `days` (query, optional) | List of trending topics with count |
| GET | `/search` | Search videos by topic | `query` (query), `page` (query, optional), `limit` (query, optional) | Paginated list of videos matching topics |

## User API

Note: The User API endpoints need to be implemented. Based on the domain model and services, the following endpoints are planned:

Base path: `/api/users`

| Method | Endpoint | Description | Request Parameters | Response |
|--------|----------|-------------|-------------------|----------|
| POST | `/` | Create user | User data in body | Created user object |
| GET | `/{user_id}` | Get user details | `user_id` (path) | User object |
| PUT | `/{user_id}` | Update user | `user_id` (path), Updated user data in body | Updated user object |
| GET | `/{user_id}/preferences` | Get user preferences | `user_id` (path) | User preferences object |
| PUT | `/{user_id}/preferences` | Update preferences | `user_id` (path), Preferences data in body | Updated preferences |

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
