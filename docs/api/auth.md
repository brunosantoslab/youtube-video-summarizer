# Authentication API

This document describes the authentication endpoints for the YouTube Video Summarizer application, focusing on the YouTube OAuth integration.

## OAuth Flow

The application uses OAuth 2.0 to authenticate with YouTube and access the user's subscription and video data. The implementation follows the standard OAuth 2.0 authorization code flow:

1. User is redirected to the Google authorization endpoint
2. User grants permission to the application
3. Google redirects back to our application with an authorization code
4. Our application exchanges the code for access and refresh tokens
5. Tokens are stored securely and used for subsequent API calls

## Endpoints

### GET /api/auth/youtube/auth-url

Generates an authorization URL for the YouTube OAuth flow.

#### Query Parameters

- `user_id` (string, required): The user ID to associate with the OAuth flow

#### Response

```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?client_id=..."
}
```

#### Status Codes

- 200: Success
- 400: Missing user_id parameter
- 500: Server error

### GET /api/auth/youtube/callback

Handles the callback from the YouTube OAuth authorization process.

#### Query Parameters

- `code` (string, required): The authorization code from Google
- `state` (string, required): The state parameter including user ID information

#### Response

```json
{
  "success": true,
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Status Codes

- 200: Success
- 400: Invalid or missing parameters
- 401: Authorization failed
- 500: Server error

### GET /api/auth/youtube/status

Checks the authentication status for a user.

#### Query Parameters

- `user_id` (string, required): The user ID to check

#### Response

```json
{
  "authenticated": true,
  "scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
  "expires_at": "2023-05-01T12:00:00Z"
}
```

#### Status Codes

- 200: Success
- 400: Missing user_id parameter
- 404: User not found
- 500: Server error

### POST /api/auth/youtube/refresh

Refreshes the access token for a user.

#### Request Body

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Response

```json
{
  "success": true,
  "expires_at": "2023-05-01T12:00:00Z"
}
```

#### Status Codes

- 200: Success
- 400: Invalid or missing parameters
- 401: Refresh token invalid or expired
- 404: User not found
- 500: Server error

### DELETE /api/auth/youtube/revoke

Revokes the authorization for a user.

#### Request Body

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Response

```json
{
  "success": true
}
```

#### Status Codes

- 200: Success
- 400: Invalid or missing parameters
- 404: User not found
- 500: Server error

## Implementation Details

The authentication service is implemented as a decoupled service with the following components:

- **OAuth2Service**: Handles the OAuth flow and token management
- **TokenEncryptionService**: Securely encrypts and decrypts tokens
- **TokenRepository**: Stores encrypted tokens in the database

The service includes automatic token refresh mechanisms and handling of expired tokens, ensuring seamless API access for users without requiring re-authorization for every request.

---

**Author**: Bruno Santos  
**Created**: April 29, 2025  
**Last Updated**: April 29, 2025
