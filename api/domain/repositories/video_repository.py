# api/domain/repositories/video_repository.py
from abc import abstractmethod
from typing import Optional, List

from domain.models.video import Video, VideoStatus
from domain.repositories.base_repository import IRepository


class IVideoRepository(IRepository[Video]):
    """Repository interface for Video entity"""
    
    @abstractmethod
    def get_by_youtube_id(self, youtube_id: str) -> Optional[Video]:
        """Get a video by YouTube ID"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: VideoStatus, limit: int = 100) -> List[Video]:
        """Get videos by status"""
        pass
    
    @abstractmethod
    def get_by_channel(self, channel_id: str, limit: int = 100) -> List[Video]:
        """Get videos by channel"""
        pass