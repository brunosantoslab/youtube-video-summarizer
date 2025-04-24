# api/infrastructure/repositories/processing_repository.py
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from domain.models.processing import ProcessingTask, ProcessingStatus
from domain.repositories.processing_repository import IProcessingRepository
from infrastructure.persistence.processing_task_entity import ProcessingTaskEntity
from infrastructure.repositories.base_repository import SQLAlchemyRepository


class PostgresProcessingRepository(SQLAlchemyRepository[ProcessingTask, ProcessingTaskEntity], IProcessingRepository):
    """PostgreSQL implementation of ProcessingTask repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, ProcessingTaskEntity)
    
    def get_by_video_id(self, video_id: uuid.UUID) -> List[ProcessingTask]:
        entities = self.session.query(ProcessingTaskEntity).filter(
            ProcessingTaskEntity.video_id == video_id
        ).all()
        return [entity.to_domain() for entity in entities]
    
    def get_by_type_and_status(
        self, 
        task_type: str, 
        status: ProcessingStatus,
        limit: int = 100
    ) -> List[ProcessingTask]:
        entities = self.session.query(ProcessingTaskEntity).filter(
            ProcessingTaskEntity.task_type == task_type,
            ProcessingTaskEntity.status == status
        ).limit(limit).all()
        return [entity.to_domain() for entity in entities]
    
    def update_status(
        self,
        task_id: uuid.UUID,
        status: ProcessingStatus,
        error_message: Optional[str] = None,
        completion_percentage: Optional[float] = None
    ) -> ProcessingTask:
        entity = self.session.query(ProcessingTaskEntity).filter(
            ProcessingTaskEntity.id == task_id
        ).first()
        
        if not entity:
            raise ValueError(f"ProcessingTask with ID {task_id} not found")
        
        entity.status = status
        entity.date_modified = datetime.now()
        
        if status == ProcessingStatus.IN_PROGRESS and not entity.date_started:
            entity.date_started = datetime.now()
        
        if status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            entity.date_completed = datetime.now()
        
        if error_message is not None:
            entity.error_message = error_message
        
        if completion_percentage is not None:
            entity.completion_percentage = completion_percentage
        
        self.session.commit()
        self.session.refresh(entity)
        
        return entity.to_domain()
    
    def update_results(
        self,
        task_id: uuid.UUID,
        results: Dict[str, Any]
    ) -> ProcessingTask:
        entity = self.session.query(ProcessingTaskEntity).filter(
            ProcessingTaskEntity.id == task_id
        ).first()
        
        if not entity:
            raise ValueError(f"ProcessingTask with ID {task_id} not found")
        
        entity.results = results
        entity.date_modified = datetime.now()
        
        self.session.commit()
        self.session.refresh(entity)
        
        return entity.to_domain()