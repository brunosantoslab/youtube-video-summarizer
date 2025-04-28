# api/infrastructure/auth/youtube_oauth_service.py
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import httpx
import uuid

from config import get_settings
from domain.models.auth import OAuthToken, OAuthTokenType
from domain.repositories.auth import IOAuthTokenRepository
from infrastructure.auth.token_encryption import TokenEncryption

logger = logging.getLogger(__name__)


class YouTubeOAuthService:
    """Service for YouTube OAuth authentication"""
    
    # OAuth endpoints
    AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    REVOKE_URL = "https://oauth2.googleapis.com/revoke"
    
    # Required scopes for YouTube API
    REQUIRED_SCOPES = [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ]
    
    def __init__(
        self,
        oauth_token_repository: IOAuthTokenRepository,
        token_encryption: Optional[TokenEncryption] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None
    ):
        self.settings = get_settings()
        self.oauth_token_repository = oauth_token_repository
        self.token_encryption = token_encryption or TokenEncryption()
        
        # OAuth client settings
        self.client_id = client_id or self.settings.youtube_client_id
        self.client_secret = client_secret or self.settings.youtube_client_secret
        self.redirect_uri = redirect_uri or self.settings.youtube_redirect_uri
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate the authorization URL for YouTube OAuth
        
        Args:
            state: Random state string for security
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",  # Force to always get refresh_token
            "scope": " ".join(self.REQUIRED_SCOPES)
        }
        
        if state:
            params["state"] = state
        
        # Build URL with query parameters
        auth_url = f"{self.AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return auth_url
    
    async def exchange_code_for_token(self, authorization_code: str, user_id: uuid.UUID) -> OAuthToken:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            authorization_code: OAuth authorization code
            user_id: User ID
            
        Returns:
            OAuthToken object
        """
        # Prepare the token request
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        # Make the token request
        async with httpx.AsyncClient() as client:
            response = await client.post(self.TOKEN_URL, data=data)
            
            if response.status_code != 200:
                error_data = response.json()
                logger.error(f"Token exchange failed: {error_data}")
                raise ValueError(f"Failed to exchange code for token: {error_data.get('error_description', 'Unknown error')}")
            
            token_data = response.json()
        
        # Calculate expiration time
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        # Create token object
        token = OAuthToken(
            user_id=user_id,
            provider=OAuthTokenType.YOUTUBE,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", ""),
            token_type=token_data.get("token_type", "Bearer"),
            scope=token_data.get("scope", " ".join(self.REQUIRED_SCOPES)),
            expires_at=expires_at
        )
        
        # Save to repository
        return self.oauth_token_repository.create(token)
    
    async def refresh_token(self, token: OAuthToken) -> OAuthToken:
        """
        Refresh an expired access token
        
        Args:
            token: OAuthToken to refresh
            
        Returns:
            Updated OAuthToken
        """
        if not token.refresh_token:
            raise ValueError("Cannot refresh token without refresh_token")
        
        # Prepare the refresh request
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token"
        }
        
        # Make the refresh request
        async with httpx.AsyncClient() as client:
            response = await client.post(self.TOKEN_URL, data=data)
            
            if response.status_code != 200:
                error_data = response.json()
                logger.error(f"Token refresh failed: {error_data}")
                raise ValueError(f"Failed to refresh token: {error_data.get('error_description', 'Unknown error')}")
            
            token_data = response.json()
        
        # Calculate expiration time
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        # Update token object
        token.access_token = token_data["access_token"]
        token.token_type = token_data.get("token_type", token.token_type)
        token.scope = token_data.get("scope", token.scope)
        token.expires_at = expires_at
        
        # If a new refresh token is provided, update it
        if "refresh_token" in token_data:
            token.refresh_token = token_data["refresh_token"]
        
        # Save updated token
        return self.oauth_token_repository.update(token)
    
    async def revoke_token(self, token: OAuthToken) -> bool:
        """
        Revoke an OAuth token
        
        Args:
            token: OAuthToken to revoke
            
        Returns:
            True if successful, False otherwise
        """
        # Prepare the revoke request
        data = {
            "token": token.access_token
        }
        
        # Make the revoke request
        async with httpx.AsyncClient() as client:
            response = await client.post(self.REVOKE_URL, data=data)
            
            if response.status_code != 200:
                logger.error(f"Token revocation failed: {response.text}")
                return False
        
        # Invalidate the token in the repository
        return self.oauth_token_repository.invalidate(token.id)
    
    async def get_user_token(self, user_id: uuid.UUID) -> Optional[OAuthToken]:
        """
        Get a valid token for a user, refreshing if necessary
        
        Args:
            user_id: User ID
            
        Returns:
            Valid OAuthToken or None if not found
        """
        token = self.oauth_token_repository.get_by_user_id(user_id, OAuthTokenType.YOUTUBE)
        
        if not token:
            return None
        
        # If token is expired, refresh it
        if token.is_expired and token.refresh_token:
            try:
                token = await self.refresh_token(token)
            except Exception as e:
                logger.error(f"Failed to refresh token for user {user_id}: {str(e)}")
                return None
        
        return token
    
    def create_encrypted_state(self, user_id: uuid.UUID, redirect_path: str = "/") -> str:
        """
        Create an encrypted state for OAuth flow
        
        Args:
            user_id: User ID
            redirect_path: Path to redirect after authentication
            
        Returns:
            Encrypted state string
        """
        state_data = {
            "user_id": str(user_id),
            "redirect_path": redirect_path,
            "timestamp": datetime.now().timestamp()
        }
        
        return self.token_encryption.encrypt_token(state_data)
    
    def parse_state(self, state: str) -> Tuple[uuid.UUID, str]:
        """
        Parse an encrypted state
        
        Args:
            state: Encrypted state string
            
        Returns:
            Tuple of (user_id, redirect_path)
        """
        state_data = self.token_encryption.decrypt_token(state)
        
        # Verify timestamp (max 10 minutes)
        timestamp = state_data.get("timestamp", 0)
        if datetime.now().timestamp() - timestamp > 600:
            raise ValueError("State has expired")
        
        user_id = uuid.UUID(state_data["user_id"])
        redirect_path = state_data.get("redirect_path", "/")
        
        return user_id, redirect_path
