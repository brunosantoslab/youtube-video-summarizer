# api/infrastructure/repositories/auth/oauth_token_repository.py
from datetime import datetime
from typing import Optional, List
import uuid

from sqlalchemy.orm import Session

from domain.models.auth import OAuthToken
from domain.repositories.auth import IOAuthTokenRepository
from infrastructure.persistence.auth import OAuthTokenEntity
from infrastructure.repositories.base_repository import SQLAlchemyRepository


class PostgresOAuthTokenRepository(SQLAlchemyRepository[OAuthToken, OAuthTokenEntity], IOAuthTokenRepository):
    """PostgreSQL implementation of IOAuthTokenRepository"""
    
    def __init__(self, session: Session):
        super().__init__(session, OAuthTokenEntity)
    
    def get_by_user_id(self, user_id: uuid.UUID, provider: str) -> Optional[OAuthToken]:
        """Get a token by user ID and provider"""
        entity = self.session.query(OAuthTokenEntity).filter(
            OAuthTokenEntity.user_id == user_id,
            OAuthTokenEntity.provider == provider
        ).first()
        
        return entity.to_domain() if entity else None
    
    def get_active_tokens(self, provider: str) -> List[OAuthToken]:
        """Get all active (non-expired) tokens for a provider"""
        entities = self.session.query(OAuthTokenEntity).filter(
            OAuthTokenEntity.provider == provider,
            OAuthTokenEntity.expires_at > datetime.now()
        ).all()
        
        return [entity.to_domain() for entity in entities]
    
    def invalidate(self, token_id: uuid.UUID) -> bool:
        """Invalidate a token (mark as expired)"""
        entity = self.session.query(OAuthTokenEntity).filter(
            OAuthTokenEntity.id == token_id
        ).first()
        
        if not entity:
            return False
        
        # Mark as expired
        entity.expires_at = datetime.now()
        self.session.commit()
        
        return True