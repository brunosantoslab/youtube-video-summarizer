# api/domain/models/video.py
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid

from domain.models.common import Entity


class VideoStatus(Enum):
    NEW = "new"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Video(Entity):
    """Video entity representing a YouTube video"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        youtube_id: str = "",
        title: str = "",
        description: str = "",
        channel_id: str = "",
        channel_title: str = "",
        published_at: Optional[datetime] = None,
        duration: Optional[timedelta] = None,
        thumbnail_url: str = "",
        status: VideoStatus = VideoStatus.NEW,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        super().__init__(id, date_created, date_modified)
        self.youtube_id = youtube_id
        self.title = title
        self.description = description
        self.channel_id = channel_id
        self.channel_title = channel_title
        self.published_at = published_at or datetime.utcnow()
        self.duration = duration or timedelta(minutes=0)
        self.thumbnail_url = thumbnail_url
        self.status = status