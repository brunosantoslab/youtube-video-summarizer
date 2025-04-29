# Users API

This document describes the Users API endpoints for the YouTube Video Summarizer application.

## User Endpoints

### GET /api/users/{user_id}

Retrieves information about a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Response

```json
{
  "id": "456e7891-23c4-56d7-e891-234567891234",
  "email": "user@example.com",
  "display_name": "User Name",
  "youtube_user_id": "ytuser_123456",
  "preference_settings": {
    "summary_length": "Standard",
    "topic_highlight_count": 5,
    "default_language": "en",
    "email_notifications": false,
    "notebook_integration_enabled": true
  },
  "auth_status": {
    "youtube_authenticated": true,
    "youtube_scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
    "youtube_expires_at": "2023-05-01T12:00:00Z"
  },
  "date_created": "2023-01-01T10:00:00Z",
  "date_modified": "2023-01-15T15:30:00Z"
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

### POST /api/users

Creates a new user.

#### Request Body

```json
{
  "email": "user@example.com",
  "display_name": "User Name",
  "youtube_user_id": "ytuser_123456",
  "preference_settings": {
    "summary_length": "Standard",
    "topic_highlight_count": 5,
    "default_language": "en",
    "email_notifications": false,
    "notebook_integration_enabled": true
  }
}
```

#### Response

```json
{
  "id": "456e7891-23c4-56d7-e891-234567891234",
  "email": "user@example.com",
  "display_name": "User Name",
  "youtube_user_id": "ytuser_123456",
  "preference_settings": {
    "summary_length": "Standard",
    "topic_highlight_count": 5,
    "default_language": "en",
    "email_notifications": false,
    "notebook_integration_enabled": true
  },
  "date_created": "2023-01-01T10:00:00Z",
  "date_modified": "2023-01-01T10:00:00Z"
}
```

#### Status Codes

- 201: Created
- 400: Invalid request parameters
- 409: User with this email already exists
- 500: Server error

### PUT /api/users/{user_id}

Updates an existing user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Request Body

```json
{
  "display_name": "Updated User Name",
  "preference_settings": {
    "summary_length": "Detailed",
    "topic_highlight_count": 8,
    "default_language": "fr",
    "email_notifications": true,
    "notebook_integration_enabled": true
  }
}
```

#### Response

```json
{
  "id": "456e7891-23c4-56d7-e891-234567891234",
  "email": "user@example.com",
  "display_name": "Updated User Name",
  "youtube_user_id": "ytuser_123456",
  "preference_settings": {
    "summary_length": "Detailed",
    "topic_highlight_count": 8,
    "default_language": "fr",
    "email_notifications": true,
    "notebook_integration_enabled": true
  },
  "date_created": "2023-01-01T10:00:00Z",
  "date_modified": "2023-01-15T15:30:00Z"
}
```

#### Status Codes

- 200: Success
- 400: Invalid request parameters
- 404: User not found
- 500: Server error

### DELETE /api/users/{user_id}

Deletes a user and all associated data.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Response

```json
{
  "success": true,
  "message": "User and all associated data deleted successfully"
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

## User Preferences Endpoints

### GET /api/users/{user_id}/preferences

Retrieves the preference settings for a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Response

```json
{
  "summary_length": "Standard",
  "topic_highlight_count": 5,
  "default_language": "en",
  "email_notifications": false,
  "notebook_integration_enabled": true
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

### PUT /api/users/{user_id}/preferences

Updates the preference settings for a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Request Body

```json
{
  "summary_length": "Detailed",
  "topic_highlight_count": 8,
  "default_language": "fr",
  "email_notifications": true,
  "notebook_integration_enabled": true
}
```

#### Response

```json
{
  "summary_length": "Detailed",
  "topic_highlight_count": 8,
  "default_language": "fr",
  "email_notifications": true,
  "notebook_integration_enabled": true
}
```

#### Status Codes

- 200: Success
- 400: Invalid request parameters
- 404: User not found
- 500: Server error

## User Authentication Endpoints

### GET /api/users/{user_id}/auth-status

Retrieves the authentication status for a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Response

```json
{
  "youtube_authenticated": true,
  "youtube_scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
  "youtube_expires_at": "2023-05-01T12:00:00Z",
  "youtube_auth_url": null
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

### POST /api/users/{user_id}/revoke-auth

Revokes the YouTube authentication for a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Response

```json
{
  "success": true,
  "message": "YouTube authentication successfully revoked"
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

## User Activity Endpoints

### GET /api/users/{user_id}/activity

Retrieves recent activity for a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Query Parameters

- `limit` (integer, optional): Maximum number of activities to return (default: 20, max: 100)
- `offset` (integer, optional): Number of activities to skip (for pagination)
- `type` (string, optional): Filter by activity type (video_added, summary_generated, summary_saved)

#### Response

```json
{
  "activities": [
    {
      "id": "c3d4e5f6-7890-a1b2-c3d4-e5f67890a1b2",
      "type": "summary_generated",
      "timestamp": "2023-01-15T15:10:23Z",
      "data": {
        "summary_id": "fedcba98-7654-3210-fedc-ba9876543210",
        "video_id": "123e4567-e89b-12d3-a456-426614174000",
        "video_title": "Video Title"
      }
    },
    {
      "id": "d4e5f678-90a1-b2c3-d4e5-f67890a1b2c3",
      "type": "video_added",
      "timestamp": "2023-01-15T14:23:45Z",
      "data": {
        "video_id": "123e4567-e89b-12d3-a456-426614174000",
        "video_title": "Video Title",
        "youtube_id": "dQw4w9WgXcQ"
      }
    },
    // Additional activities...
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

### GET /api/users/{user_id}/stats

Retrieves usage statistics for a specific user.

#### Path Parameters

- `user_id` (string, required): The UUID of the user

#### Response

```json
{
  "videos_count": 38,
  "summaries_count": 45,
  "saved_summaries_count": 12,
  "topics_count": 156,
  "channels_count": 8,
  "total_video_duration": "PT25H45M30S",
  "most_common_topics": [
    {
      "name": "Machine Learning",
      "count": 15
    },
    {
      "name": "Neural Networks",
      "count": 12
    },
    {
      "name": "Deep Learning",
      "count": 10
    }
  ],
  "most_active_channels": [
    {
      "id": "UC-lHJZR3Gqxm24_Vd_AJ5Yw",
      "title": "Channel Name",
      "videos_count": 12
    },
    // Additional channels...
  ],
  "activity_by_month": [
    {
      "month": "2023-01",
      "videos_added": 15,
      "summaries_generated": 18
    },
    // Additional months...
  ]
}
```

#### Status Codes

- 200: Success
- 404: User not found
- 500: Server error

## Implementation Details

The Users API is implemented with the following components:

- **UserController**: FastAPI routes for handling user-related HTTP requests
- **UserApplicationService**: Application service for orchestrating user operations
- **UserRepository**: Data access layer for user storage and retrieval
- **UserPreferencesService**: Service for managing user preferences
- **UserActivityService**: Service for tracking and retrieving user activity

User preferences are stored as a JSON object in the database, allowing for flexible addition of new preference options without database schema changes.

User authentication status is checked on each request that requires YouTube API access, with automatic token refresh when tokens are nearing expiration.

User activity is tracked via events emitted during various operations (video addition, summary generation, etc.), with the activity data stored in a separate collection for efficient querying and pagination.

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
