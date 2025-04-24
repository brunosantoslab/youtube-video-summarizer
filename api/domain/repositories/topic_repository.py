# api/domain/repositories/topic_repository.py
from abc import abstractmethod
from typing import List
import uuid

from domain.models.topic import Topic
from domain.repositories.base_repository import IRepository


class ITopicRepository(IRepository[Topic]):
    """Repository interface for Topic entity"""
    
    @abstractmethod
    def get_by_video_id(self, video_id: uuid.UUID) -> List[Topic]:
        """Get topics for a video"""
        pass
    
    @abstractmethod
    def get_by_summary_id(self, summary_id: uuid.UUID) -> List[Topic]:
        """Get topics for a summary"""
        pass
    
    @abstractmethod
    def create_many(self, topics: List[Topic]) -> List[Topic]:
        """Create multiple topics at once"""
        pass