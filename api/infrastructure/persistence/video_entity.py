# api/infrastructure/persistence/video_entity.py
from sqlalchemy import Column, String, Enum as SQLAEnum, Interval
from sqlalchemy.dialects.postgresql import UUID
import uuid

from domain.models.video import Video, VideoStatus
from infrastructure.persistence.base import Base, BaseEntity


class VideoEntity(Base, BaseEntity):
    """SQLAlchemy entity for Video"""
    
    __tablename__ = "videos"
    
    youtube_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    channel_id = Column(String, nullable=False)
    channel_title = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    duration = Column(Interval, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(SQLAEnum(VideoStatus), nullable=False, default=VideoStatus.NEW)
    
    @staticmethod
    def from_domain(video: Video) -> "VideoEntity":
        """Convert domain entity to ORM entity"""
        return VideoEntity(
            id=video.id,
            youtube_id=video.youtube_id,
            title=video.title,
            description=video.description,
            channel_id=video.channel_id,
            channel_title=video.channel_title,
            published_at=video.published_at,
            duration=video.duration,
            thumbnail_url=video.thumbnail_url,
            status=video.status,
            date_created=video.date_created,
            date_modified=video.date_modified
        )
    
    def to_domain(self) -> Video:
        """Convert ORM entity to domain entity"""
        return Video(
            id=self.id,
            youtube_id=self.youtube_id,
            title=self.title,
            description=self.description,
            channel_id=self.channel_id,
            channel_title=self.channel_title,
            published_at=self.published_at,
            duration=self.duration,
            thumbnail_url=self.thumbnail_url,
            status=self.status,
            date_created=self.date_created,
            date_modified=self.date_modified
        )