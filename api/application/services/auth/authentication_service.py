# api/application/services/auth/authentication_service.py
import logging
import uuid
from typing import Optional, Dict, Any, Tuple

from domain.models.auth import OAuthToken
from domain.repositories.auth import IOAuthTokenRepository
from infrastructure.auth.youtube_oauth_service import YouTubeOAuthService

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for handling user authentication flows"""
    
    def __init__(
        self,
        youtube_oauth_service: YouTubeOAuthService,
        oauth_token_repository: IOAuthTokenRepository
    ):
        self.youtube_oauth_service = youtube_oauth_service
        self.oauth_token_repository = oauth_token_repository
    
    def get_youtube_auth_url(self, user_id: uuid.UUID, redirect_path: str = "/") -> str:
        """
        Get the YouTube authentication URL
        
        Args:
            user_id: User ID
            redirect_path: Path to redirect after authentication
            
        Returns:
            Authentication URL
        """
        # Create encrypted state with user ID and redirect path
        state = self.youtube_oauth_service.create_encrypted_state(user_id, redirect_path)
        
        # Get authorization URL
        return self.youtube_oauth_service.get_authorization_url(state)
    
    async def handle_youtube_callback(self, code: str, state: str) -> Tuple[bool, str]:
        """
        Handle YouTube OAuth callback
        
        Args:
            code: Authorization code
            state: State parameter
            
        Returns:
            Tuple of (success, redirect_path)
        """
        try:
            # Parse state to get user ID and redirect path
            user_id, redirect_path = self.youtube_oauth_service.parse_state(state)
            
            # Exchange code for token
            await self.youtube_oauth_service.exchange_code_for_token(code, user_id)
            
            return True, redirect_path
            
        except Exception as e:
            logger.error(f"YouTube OAuth callback failed: {str(e)}")
            return False, "/"
    
    async def get_youtube_token(self, user_id: uuid.UUID) -> Optional[OAuthToken]:
        """
        Get a valid YouTube token for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Valid token or None
        """
        return await self.youtube_oauth_service.get_user_token(user_id)
    
    def is_youtube_authenticated(self, user_id: uuid.UUID) -> bool:
        """
        Check if a user is authenticated with YouTube
        
        Args:
            user_id: User ID
            
        Returns:
            True if authenticated, False otherwise
        """
        # Get token without refreshing
        token = self.oauth_token_repository.get_by_user_id(user_id, "youtube")
        
        # Check if token exists and is not expired
        return token is not None and not token.is_expired
    
    async def revoke_youtube_access(self, user_id: uuid.UUID) -> bool:
        """
        Revoke YouTube access for a user
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        token = self.oauth_token_repository.get_by_user_id(user_id, "youtube")
        
        if not token:
            return False
        
        return await self.youtube_oauth_service.revoke_token(token)