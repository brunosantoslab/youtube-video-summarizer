# api/infrastructure/persistence/saved_summary_entity.py
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from domain.models.saved_summary import SavedSummary
from infrastructure.persistence.base import Base, BaseEntity


class SavedSummaryEntity(Base, BaseEntity):
    """SQLAlchemy entity for SavedSummary"""
    
    __tablename__ = "saved_summaries"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    summary_id = Column(UUID(as_uuid=True), ForeignKey("summaries.id"), nullable=False)
    notes = Column(String, nullable=True)
    folder_name = Column(String, nullable=True)
    date_saved = Column(DateTime, nullable=False, default=datetime.now)
    
    @staticmethod
    def from_domain(saved_summary: SavedSummary) -> "SavedSummaryEntity":
        """Convert domain entity to ORM entity"""
        return SavedSummaryEntity(
            id=saved_summary.id,
            user_id=saved_summary.user_id,
            summary_id=saved_summary.summary_id,
            notes=saved_summary.notes,
            folder_name=saved_summary.folder_name,
            date_saved=saved_summary.date_saved,
            date_created=saved_summary.date_created,
            date_modified=saved_summary.date_modified
        )
    
    def to_domain(self) -> SavedSummary:
        """Convert ORM entity to domain entity"""
        return SavedSummary(
            id=self.id,
            user_id=self.user_id,
            summary_id=self.summary_id,
            notes=self.notes,
            folder_name=self.folder_name,
            date_saved=self.date_saved,
            date_created=self.date_created,
            date_modified=self.date_modified
        )