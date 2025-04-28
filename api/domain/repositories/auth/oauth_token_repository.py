# api/domain/repositories/auth/oauth_token_repository.py
from abc import abstractmethod
from typing import Optional, List
import uuid

from domain.models.auth import OAuthToken
from domain.repositories.base_repository import IRepository


class IOAuthTokenRepository(IRepository[OAuthToken]):
    """Repository interface for OAuthToken entity"""
    
    @abstractmethod
    def get_by_user_id(self, user_id: uuid.UUID, provider: str) -> Optional[OAuthToken]:
        """
        Get a token by user ID and provider
        
        Args:
            user_id: User ID
            provider: Provider name
            
        Returns:
            OAuthToken or None if not found
        """
        pass
    
    @abstractmethod
    def get_active_tokens(self, provider: str) -> List[OAuthToken]:
        """
        Get all active (non-expired) tokens for a provider
        
        Args:
            provider: Provider name
            
        Returns:
            List of OAuthToken
        """
        pass
    
    @abstractmethod
    def invalidate(self, token_id: uuid.UUID) -> bool:
        """
        Invalidate a token (delete or mark as expired)
        
        Args:
            token_id: Token ID
            
        Returns:
            True if successful, False otherwise
        """
        pass