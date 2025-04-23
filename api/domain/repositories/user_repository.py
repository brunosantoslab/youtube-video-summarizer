# api/domain/repositories/user_repository.py
from abc import abstractmethod
from typing import Optional, List
import uuid

from domain.models.user import User
from domain.repositories.base_repository import IRepository


class IUserRepository(IRepository[User]):
    """Repository interface for User entity"""
    
    @abstractmethod
    def get_by_youtube_id(self, youtube_id: str) -> Optional[User]:
        """Get a user by YouTube ID"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        pass