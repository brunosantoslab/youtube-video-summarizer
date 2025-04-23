# api/infrastructure/persistence/user_entity.py
from sqlalchemy import Column, String, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from domain.models.user import User, UserPreferences
from infrastructure.persistence.base import Base, BaseEntity


class UserEntity(Base, BaseEntity):
    """SQLAlchemy entity for User"""
    
    __tablename__ = "users"
    
    email = Column(String, unique=True, nullable=False)
    youtube_user_id = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    preferences_json = Column(JSON, nullable=False, default=dict)
    
    @staticmethod
    def from_domain(user: User) -> "UserEntity":
        """Convert domain entity to ORM entity"""
        return UserEntity(
            id=user.id,
            email=user.email,
            youtube_user_id=user.youtube_user_id,
            display_name=user.display_name,
            preferences_json=user.preference_settings.to_dict(),
            date_created=user.date_created,
            date_modified=user.date_modified
        )
    
    def to_domain(self) -> User:
        """Convert ORM entity to domain entity"""
        return User(
            id=self.id,
            email=self.email,
            youtube_user_id=self.youtube_user_id,
            display_name=self.display_name,
            preference_settings=UserPreferences.from_dict(self.preferences_json),
            date_created=self.date_created,
            date_modified=self.date_modified
        )