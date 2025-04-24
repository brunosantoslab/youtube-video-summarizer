# api/infrastructure/persistence/summary_entity.py
from sqlalchemy import Column, String, ForeignKey, JSONB
from sqlalchemy.dialects.postgresql import UUID

from domain.models.summary import Summary, SummaryMetadata
from infrastructure.persistence.base import Base, BaseEntity


class SummaryEntity(Base, BaseEntity):
    """SQLAlchemy entity for Summary"""
    
    __tablename__ = "summaries"
    
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    content = Column(String, nullable=False)
    model_provider = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    processing_metadata = Column(JSONB, nullable=False)
    
    @staticmethod
    def from_domain(summary: Summary) -> "SummaryEntity":
        """Convert domain entity to ORM entity"""
        return SummaryEntity(
            id=summary.id,
            video_id=summary.video_id,
            content=summary.content,
            model_provider=summary.model_provider,
            model_version=summary.model_version,
            processing_metadata=summary.processing_metadata.to_dict(),
            date_created=summary.date_created,
            date_modified=summary.date_modified
        )
    
    def to_domain(self) -> Summary:
        """Convert ORM entity to domain entity"""
        metadata = SummaryMetadata.from_dict(self.processing_metadata)
        
        return Summary(
            id=self.id,
            video_id=self.video_id,
            content=self.content,
            model_provider=self.model_provider,
            model_version=self.model_version,
            processing_metadata=metadata,
            date_created=self.date_created,
            date_modified=self.date_modified
        )