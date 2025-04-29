# api/infrastructure/persistence/auth/oauth_token_entity.py
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from domain.models.auth import OAuthToken
from infrastructure.persistence.base import Base, BaseEntity


class OAuthTokenEntity(Base, BaseEntity):
    """SQLAlchemy entity for OAuthToken"""
    
    __tablename__ = "oauth_tokens"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_type = Column(String, nullable=False, default="Bearer")
    scope = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserEntity", back_populates="oauth_tokens")
    
    @staticmethod
    def from_domain(domain_obj: OAuthToken) -> "OAuthTokenEntity":
        """Convert domain entity to ORM entity"""
        return OAuthTokenEntity(
            id=domain_obj.id,
            user_id=domain_obj.user_id,
            provider=domain_obj.provider,
            access_token=domain_obj.access_token,
            refresh_token=domain_obj.refresh_token,
            token_type=domain_obj.token_type,
            scope=domain_obj.scope,
            expires_at=domain_obj.expires_at,
            date_created=domain_obj.date_created,
            date_modified=domain_obj.date_modified
        )
    
    def to_domain(self) -> OAuthToken:
        """Convert ORM entity to domain entity"""
        return OAuthToken(
            id=self.id,
            user_id=self.user_id,
            provider=self.provider,
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            token_type=self.token_type,
            scope=self.scope,
            expires_at=self.expires_at,
            created_at=self.date_created,
            updated_at=self.date_modified
        )