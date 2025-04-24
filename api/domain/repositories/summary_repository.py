# api/domain/repositories/summary_repository.py
from abc import abstractmethod
from typing import Optional, List
import uuid

from domain.models.summary import Summary
from domain.repositories.base_repository import IRepository


class ISummaryRepository(IRepository[Summary]):
    """Repository interface for Summary entity"""
    
    @abstractmethod
    def get_by_video_id(self, video_id: uuid.UUID) -> Optional[Summary]:
        """Get a summary by video ID"""
        pass
    
    @abstractmethod
    def get_latest_by_video_id(self, video_id: uuid.UUID) -> Optional[Summary]:
        """Get the latest summary for a video"""
        pass
    
    @abstractmethod
    def get_saved_by_user(self, user_id: uuid.UUID, limit: int = 100) -> List[Summary]:
        """Get summaries saved by a user"""
        pass