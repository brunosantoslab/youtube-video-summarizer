# api/infrastructure/persistence/transcript_entity.py
from sqlalchemy import Column, String, Float, JSON, ForeignKey, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import json
from typing import List

from domain.models.transcript import (
    Transcript, TranscriptSourceType, ProcessingStatus, 
    TranscriptSegment, TranscriptMetadata
)
from infrastructure.persistence.base import Base, BaseEntity


class TranscriptEntity(Base, BaseEntity):
    """SQLAlchemy entity for Transcript"""
    
    __tablename__ = "transcripts"
    
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    content = Column(String, nullable=True)
    segments = Column(JSONB, nullable=True)
    source_type = Column(SQLAEnum(TranscriptSourceType), nullable=False)
    language_code = Column(String, nullable=False)
    processing_status = Column(SQLAEnum(ProcessingStatus), nullable=False)
    transcript_metadata = Column(JSONB, nullable=False)
    
    @staticmethod
    def from_domain(transcript: Transcript) -> "TranscriptEntity":
        """Convert domain entity to ORM entity"""
        segments_json = [s.to_dict() for s in transcript.segments] if transcript.segments else []
        
        return TranscriptEntity(
            id=transcript.id,
            video_id=transcript.video_id,
            content=transcript.content,
            segments=segments_json,
            source_type=transcript.source_type,
            language_code=transcript.language_code,
            processing_status=transcript.processing_status,
            transcript_metadata=transcript.metadata.to_dict(),
            date_created=transcript.date_created,
            date_modified=transcript.date_modified
        )
    
    def to_domain(self) -> Transcript:
        """Convert ORM entity to domain entity"""
        segments = [
            TranscriptSegment.from_dict(segment_data)
            for segment_data in self.segments
        ] if self.segments else []
        
        metadata = TranscriptMetadata.from_dict(self.transcript_metadata)
        
        return Transcript(
            id=self.id,
            video_id=self.video_id,
            content=self.content,
            segments=segments,
            source_type=self.source_type,
            language_code=self.language_code,
            processing_status=self.processing_status,
            metadata=metadata,
            date_created=self.date_created,
            date_modified=self.date_modified
        )