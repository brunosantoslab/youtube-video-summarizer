# Notebooks API

This document describes the Notebooks API endpoints for the YouTube Video Summarizer application, which enable integration with Jupyter notebooks and similar environments.

## Notebook Integration Endpoints

### GET /api/notebooks/embed/{video_id}

Generates an embeddable HTML snippet for a video with its summary.

#### Path Parameters

- `video_id` (string, required): The UUID of the video

#### Query Parameters

- `summary_id` (string, optional): Specific summary ID to use (defaults to latest)
- `include_transcript` (boolean, optional): Whether to include the transcript (default: false)
- `include_topics` (boolean, optional): Whether to include extracted topics (default: true)
- `width` (integer, optional): Width of the embedded player (default: 640)
- `height` (integer, optional): Height of the embedded player (default: 360)
- `theme` (string, optional): Color theme to use (light, dark, default: light)

#### Response

```json
{
  "html": "<div class=\"yvs-embed\" data-video-id=\"123e4567-e89b-12d3-a456-426614174000\">...</div>",
  "javascript": "https://api.yvs.example.com/static/embed.js",
  "css": "https://api.yvs.example.com/static/embed.css"
}
```

#### Status Codes

- 200: Success
- 404: Video not found
- 500: Server error

### GET /api/notebooks/markdown/{video_id}

Generates a Markdown representation of a video summary for use in notebooks.

#### Path Parameters

- `video_id` (string, required): The UUID of the video

#### Query Parameters

- `summary_id` (string, optional): Specific summary ID to use (defaults to latest)
- `include_transcript` (boolean, optional): Whether to include the transcript (default: false)
- `include_topics` (boolean, optional): Whether to include extracted topics (default: true)
- `format` (string, optional): Markdown format (github, jupyter, default: jupyter)

#### Response

```json
{
  "markdown": "# Video Title\n\n[![Thumbnail](https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg)](https://www.youtube.com/watch?v=dQw4w9WgXcQ)\n\n## Summary\n\nThis is a comprehensive summary of the video content...\n\n## Topics\n\n- Machine Learning (95%)\n- Neural Networks (87%)\n- Deep Learning (82%)\n\n## Transcript\n\n[00:00:00] Speaker 1: Hello and welcome to this video...",
  "download_url": "https://api.yvs.example.com/notebooks/download/123e4567-e89b-12d3-a456-426614174000?format=md"
}
```

#### Status Codes

- 200: Success
- 404: Video not found
- 500: Server error

### GET /api/notebooks/ipynb/{video_id}

Generates a Jupyter notebook (.ipynb) file for a video with its summary.

#### Path Parameters

- `video_id` (string, required): The UUID of the video

#### Query Parameters

- `summary_id` (string, optional): Specific summary ID to use (defaults to latest)
- `include_transcript` (boolean, optional): Whether to include the transcript (default: false)
- `include_topics` (boolean, optional): Whether to include extracted topics (default: true)
- `include_code_cells` (boolean, optional): Whether to include example code cells for analysis (default: true)

#### Response

Binary file download (application/x-ipynb+json)

```
HTTP/1.1 200 OK
Content-Disposition: attachment; filename="Video_Title.ipynb"
Content-Type: application/x-ipynb+json

[Binary content of the .ipynb file]
```

#### Status Codes

- 200: Success
- 404: Video not found
- 500: Server error

### POST /api/notebooks/collection

Creates a notebook collection from multiple videos.

#### Request Body

```json
{
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "title": "Machine Learning Video Collection",
  "description": "A collection of videos about machine learning concepts",
  "video_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "234f5678-f90a-12b3-c456-726614174001",
    "345g6789-0a1b-23c4-d567-8266141740e2"
  ],
  "include_transcript": false,
  "include_topics": true,
  "format": "ipynb"
}
```

#### Response

```json
{
  "collection_id": "d5e6f789-0a1b-2c3d-e4f5-6789a0b1c2d3",
  "title": "Machine Learning Video Collection",
  "video_count": 3,
  "download_url": "https://api.yvs.example.com/notebooks/collection/d5e6f789-0a1b-2c3d-e4f5-6789a0b1c2d3"
}
```

#### Status Codes

- 201: Created
- 400: Invalid request parameters
- 404: One or more videos not found
- 500: Server error

### GET /api/notebooks/collection/{collection_id}

Retrieves a previously created notebook collection.

#### Path Parameters

- `collection_id` (string, required): The UUID of the collection

#### Response

```json
{
  "id": "d5e6f789-0a1b-2c3d-e4f5-6789a0b1c2d3",
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "title": "Machine Learning Video Collection",
  "description": "A collection of videos about machine learning concepts",
  "videos": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Video Title 1",
      "youtube_id": "dQw4w9WgXcQ",
      "channel_title": "Channel Name",
      "summary_id": "fedcba98-7654-3210-fedc-ba9876543210"
    },
    // Additional videos...
  ],
  "created_at": "2023-01-16T10:30:45Z",
  "format": "ipynb",
  "download_url": "https://api.yvs.example.com/notebooks/collection/d5e6f789-0a1b-2c3d-e4f5-6789a0b1c2d3"
}
```

#### Status Codes

- 200: Success
- 404: Collection not found
- 500: Server error

## Sharing Endpoints

### POST /api/notebooks/share

Creates a shareable link for a video summary or collection.

#### Request Body

```json
{
  "user_id": "456e7891-23c4-56d7-e891-234567891234",
  "resource_type": "video",
  "resource_id": "123e4567-e89b-12d3-a456-426614174000",
  "expiration_days": 30,
  "access_type": "public"
}
```

#### Response

```json
{
  "share_id": "abcdef12345",
  "share_url": "https://share.yvs.example.com/s/abcdef12345",
  "resource_type": "video",
  "resource_id": "123e4567-e89b-12d3-a456-426614174000",
  "expires_at": "2023-02-15T10:30:45Z",
  "access_type": "public",
  "embed_html": "<iframe src=\"https://share.yvs.example.com/embed/abcdef12345\" width=\"640\" height=\"480\" frameborder=\"0\"></iframe>"
}
```

#### Status Codes

- 201: Created
- 400: Invalid request parameters
- 404: Resource not found
- 500: Server error

### GET /api/notebooks/share/{share_id}

Retrieves information about a shared resource.

#### Path Parameters

- `share_id` (string, required): The ID of the shared resource

#### Response

```json
{
  "share_id": "abcdef12345",
  "resource_type": "video",
  "resource": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Video Title",
    "youtube_id": "dQw4w9WgXcQ",
    "channel_title": "Channel Name",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
    "summary": {
      "id": "fedcba98-7654-3210-fedc-ba9876543210",
      "content": "This is a comprehensive summary of the video content...",
      "model_provider": "openai",
      "date_created": "2023-01-15T15:10:23Z"
    }
  },
  "created_by": "User Name",
  "created_at": "2023-01-16T10:30:45Z",
  "expires_at": "2023-02-15T10:30:45Z",
  "access_type": "public"
}
```

#### Status Codes

- 200: Success
- 404: Shared resource not found or expired
- 500: Server error

### DELETE /api/notebooks/share/{share_id}

Deletes a shared resource.

#### Path Parameters

- `share_id` (string, required): The ID of the shared resource

#### Response

```json
{
  "success": true,
  "message": "Shared resource deleted successfully"
}
```

#### Status Codes

- 200: Success
- 404: Shared resource not found
- 500: Server error

## Implementation Details

The Notebooks API is implemented with the following components:

- **NotebookController**: FastAPI routes for handling notebook-related HTTP requests
- **NotebookApplicationService**: Application service for orchestrating notebook operations
- **NotebookGenerator**: Service for generating different notebook formats
- **EmbedGenerator**: Service for generating embeddable content
- **ShareService**: Service for managing shared resources

The notebook generation process uses templates for different output formats:

1. Jupyter notebooks (.ipynb) are generated using the nbformat library
2. Markdown files are generated using templates with appropriate formatting
3. Embeddable HTML is generated with responsive design for integration into web pages

For video collections, the system generates a single notebook that includes all selected videos with their summaries, organized into sections with appropriate headings and navigation.

Shared resources are secured with:
1. Unique, hard-to-guess share IDs
2. Optional expiration dates
3. Access control (public, private with link)
4. Rate limiting to prevent abuse

The embed functionality uses a lightweight JavaScript widget that loads content dynamically to minimize the impact on the host page's performance.

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
