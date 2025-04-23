# api/infrastructure/repositories/transcript_repository.py
from typing import Optional, List
import uuid

from sqlalchemy.orm import Session

from domain.models.transcript import Transcript, ProcessingStatus
from domain.repositories.transcript_repository import ITranscriptRepository
from infrastructure.persistence.transcript_entity import TranscriptEntity
from infrastructure.repositories.base_repository import SQLAlchemyRepository


class PostgresTranscriptRepository(SQLAlchemyRepository[Transcript, TranscriptEntity], ITranscriptRepository):
    """PostgreSQL implementation of Transcript repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, TranscriptEntity)
    
    def get_by_video_id(self, video_id: uuid.UUID) -> Optional[Transcript]:
        entity = self.session.query(TranscriptEntity).filter(TranscriptEntity.video_id == video_id).first()
        return entity.to_domain() if entity else None
    
    def get_by_status(self, status: ProcessingStatus, limit: int = 100) -> List[Transcript]:
        entities = self.session.query(TranscriptEntity).filter(
            TranscriptEntity.processing_status == status
        ).limit(limit).all()
        return [entity.to_domain() for entity in entities]