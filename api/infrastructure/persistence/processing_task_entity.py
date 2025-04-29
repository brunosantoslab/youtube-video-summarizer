# api/infrastructure/persistence/processing_task_entity.py
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum as SQLAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID

from domain.models.processing import ProcessingTask, ProcessingStatus
from infrastructure.persistence.base import Base, BaseEntity


class ProcessingTaskEntity(Base, BaseEntity):
    """SQLAlchemy entity for ProcessingTask"""
    
    __tablename__ = "processing_tasks"
    
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    task_type = Column(String, nullable=False)
    status = Column(SQLAEnum(ProcessingStatus), nullable=False)
    error_message = Column(String, nullable=True)
    completion_percentage = Column(Float, nullable=False, default=0.0)
    task_metadata = Column(JSON, nullable=False, default=dict)
    results = Column(JSON, nullable=False, default=dict)
    date_started = Column(DateTime, nullable=True)
    date_completed = Column(DateTime, nullable=True)
    
    @staticmethod
    def from_domain(task: ProcessingTask) -> "ProcessingTaskEntity":
        """Convert domain entity to ORM entity"""
        return ProcessingTaskEntity(
            id=task.id,
            video_id=task.video_id,
            task_type=task.task_type,
            status=task.status,
            error_message=task.error_message,
            completion_percentage=task.completion_percentage,
            task_metadata=task.task_metadata,
            results=task.results,
            date_started=task.date_started,
            date_completed=task.date_completed,
            date_created=task.date_created,
            date_modified=task.date_modified
        )
    
    def to_domain(self) -> ProcessingTask:
        """Convert ORM entity to domain entity"""
        return ProcessingTask(
            id=self.id,
            video_id=self.video_id,
            task_type=self.task_type,
            status=self.status,
            error_message=self.error_message,
            completion_percentage=self.completion_percentage,
            task_metadata=self.task_metadata,
            results=self.results,
            date_started=self.date_started,
            date_completed=self.date_completed,
            date_created=self.date_created,
            date_modified=self.date_modified
        )