# api/infrastructure/repositories/topic_repository.py
from typing import List
import uuid

from sqlalchemy.orm import Session

from domain.models.topic import Topic
from domain.repositories.topic_repository import ITopicRepository
from infrastructure.persistence.topic_entity import TopicEntity
from infrastructure.repositories.base_repository import SQLAlchemyRepository


class PostgresTopicRepository(SQLAlchemyRepository[Topic, TopicEntity], ITopicRepository):
    """PostgreSQL implementation of Topic repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, TopicEntity)
    
    def get_by_video_id(self, video_id: uuid.UUID) -> List[Topic]:
        entities = self.session.query(TopicEntity).filter(
            TopicEntity.video_id == video_id
        ).all()
        return [entity.to_domain() for entity in entities]
    
    def get_by_summary_id(self, summary_id: uuid.UUID) -> List[Topic]:
        entities = self.session.query(TopicEntity).filter(
            TopicEntity.summary_id == summary_id
        ).all()
        return [entity.to_domain() for entity in entities]
    
    def create_many(self, topics: List[Topic]) -> List[Topic]:
        """Create multiple topics at once"""
        entities = [TopicEntity.from_domain(topic) for topic in topics]
        self.session.add_all(entities)
        self.session.commit()
        
        # Refresh to get generated IDs
        for entity in entities:
            self.session.refresh(entity)
        
        return [entity.to_domain() for entity in entities]