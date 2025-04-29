# YouTube Video Summarizer API Documentation

This directory contains documentation for the YouTube Video Summarizer API endpoints.

## Table of Contents

1. [Authentication API](auth.md)
2. [Video Management API](videos.md)
3. [Transcript API](transcripts.md)
4. [Summary API](summaries.md)
5. [Topics API](topics.md)
6. [Users API](users.md)

## Authentication API

Documentation for authentication endpoints including YouTube OAuth integration.

*Coming soon*

## Video Management API

Documentation for video management endpoints including fetching, searching, and tracking videos.

*Coming soon*

## Transcript API

Documentation for transcript extraction and management endpoints.

*Coming soon*

## Summary API

Documentation for summary generation and retrieval endpoints.

*Coming soon*

## Topics API

Documentation for topic extraction and management endpoints.

*Coming soon*

## Creating API Documentation

For developers: Please document all API endpoints by creating Markdown files in this directory
with the following structure:

```markdown
# Endpoint Group Name

## GET /api/resource

Fetches a specific resource.

### Parameters

- `id` (string, required): The ID of the resource to fetch

### Response

```json
{
  "id": "123",
  "name": "Resource name",
  "description": "Resource description"
}
```

### Status Codes

- 200: Success
- 404: Resource not found
- 500: Server error
```

---

**Author**: Bruno Santos  
**Created**: April 29, 2025
