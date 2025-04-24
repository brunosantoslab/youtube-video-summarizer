# api/infrastructure/repositories/summary_repository.py
from typing import Optional, List
import uuid

from sqlalchemy import desc
from sqlalchemy.orm import Session

from domain.models.summary import Summary
from domain.repositories.summary_repository import ISummaryRepository
from infrastructure.persistence.summary_entity import SummaryEntity
from infrastructure.persistence.saved_summary_entity import SavedSummaryEntity
from infrastructure.repositories.base_repository import SQLAlchemyRepository


class PostgresSummaryRepository(SQLAlchemyRepository[Summary, SummaryEntity], ISummaryRepository):
    """PostgreSQL implementation of Summary repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, SummaryEntity)
    
    def get_by_video_id(self, video_id: uuid.UUID) -> Optional[Summary]:
        entity = self.session.query(SummaryEntity).filter(
            SummaryEntity.video_id == video_id
        ).first()
        return entity.to_domain() if entity else None
    
    def get_latest_by_video_id(self, video_id: uuid.UUID) -> Optional[Summary]:
        entity = self.session.query(SummaryEntity).filter(
            SummaryEntity.video_id == video_id
        ).order_by(desc(SummaryEntity.date_created)).first()
        return entity.to_domain() if entity else None
    
    def get_saved_by_user(self, user_id: uuid.UUID, limit: int = 100) -> List[Summary]:
        """Get summaries saved by a user
        
        This method joins with the saved_summaries table to find all summaries
        that have been saved by the specified user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of results to return
            
        Returns:
            List of Summary objects saved by the user
        """
        entities = self.session.query(SummaryEntity).join(
            SavedSummaryEntity,
            SavedSummaryEntity.summary_id == SummaryEntity.id
        ).filter(
            SavedSummaryEntity.user_id == user_id
        ).order_by(
            desc(SavedSummaryEntity.date_saved)
        ).limit(limit).all()
        
        return [entity.to_domain() for entity in entities]