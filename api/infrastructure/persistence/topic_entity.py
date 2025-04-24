# api/infrastructure/persistence/topic_entity.py
from sqlalchemy import Column, String, Float, ForeignKey, Interval
from sqlalchemy.dialects.postgresql import UUID
import uuid

from domain.models.topic import Topic
from infrastructure.persistence.base import Base, BaseEntity


class TopicEntity(Base, BaseEntity):
    """SQLAlchemy entity for Topic"""
    
    __tablename__ = "topics"
    
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    summary_id = Column(UUID(as_uuid=True), ForeignKey("summaries.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    relevance = Column(Float, nullable=False, default=0.0)
    start_time = Column(Interval, nullable=True)
    end_time = Column(Interval, nullable=True)
    
    @staticmethod
    def from_domain(topic: Topic) -> "TopicEntity":
        """Convert domain entity to ORM entity"""
        return TopicEntity(
            id=topic.id,
            video_id=topic.video_id,
            summary_id=topic.summary_id,
            name=topic.name,
            description=topic.description,
            relevance=topic.relevance,
            start_time=topic.start_time,
            end_time=topic.end_time,
            date_created=topic.date_created,
            date_modified=topic.date_modified
        )
    
    def to_domain(self) -> Topic:
        """Convert ORM entity to domain entity"""
        return Topic(
            id=self.id,
            video_id=self.video_id,
            summary_id=self.summary_id,
            name=self.name,
            description=self.description,
            relevance=self.relevance,
            start_time=self.start_time,
            end_time=self.end_time,
            date_created=self.date_created,
            date_modified=self.date_modified
        )