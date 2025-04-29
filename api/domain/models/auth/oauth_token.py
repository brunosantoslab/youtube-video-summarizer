# api/domain/models/auth/oauth_token.py
from datetime import datetime
from typing import Optional
import uuid

from domain.models.common import Entity


class OAuthTokenType:
    """Types of OAuth tokens"""
    YOUTUBE = "youtube"
    GOOGLE = "google"


class OAuthToken(Entity):
    """OAuth token entity for storing authentication tokens"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        provider: str = OAuthTokenType.YOUTUBE,
        access_token: str = "",
        refresh_token: str = "",
        token_type: str = "Bearer",
        scope: str = "",
        expires_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self.user_id = user_id
        self.provider = provider
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.scope = scope
        self.expires_at = expires_at

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired"""
        if not self.expires_at:
            return True
        return self.expires_at <= datetime.now()
    
    @property
    def authorization_header(self) -> str:
        """Get the authorization header value"""
        return f"{self.token_type} {self.access_token}"
