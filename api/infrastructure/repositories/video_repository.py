# api/infrastructure/repositories/video_repository.py
from typing import Optional, List

from sqlalchemy.orm import Session

from domain.models.video import Video, VideoStatus
from domain.repositories.video_repository import IVideoRepository
from infrastructure.persistence.video_entity import VideoEntity
from infrastructure.repositories.base_repository import SQLAlchemyRepository


class PostgresVideoRepository(SQLAlchemyRepository[Video, VideoEntity], IVideoRepository):
    """PostgreSQL implementation of Video repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, VideoEntity)
    
    def get_by_youtube_id(self, youtube_id: str) -> Optional[Video]:
        entity = self.session.query(VideoEntity).filter(VideoEntity.youtube_id == youtube_id).first()
        return entity.to_domain() if entity else None
    
    def get_by_status(self, status: VideoStatus, limit: int = 100) -> List[Video]:
        entities = self.session.query(VideoEntity).filter(VideoEntity.status == status).limit(limit).all()
        return [entity.to_domain() for entity in entities]
    
    def get_by_channel(self, channel_id: str, limit: int = 100) -> List[Video]:
        entities = self.session.query(VideoEntity).filter(VideoEntity.channel_id == channel_id).limit(limit).all()
        return [entity.to_domain() for entity in entities]