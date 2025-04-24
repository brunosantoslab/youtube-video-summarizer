# api/domain/models/processing.py
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import uuid

from domain.models.common import Entity


class ProcessingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingTask(Entity):
    """Entity representing a background processing task"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        video_id: Optional[uuid.UUID] = None,
        task_type: str = "",
        status: ProcessingStatus = ProcessingStatus.PENDING,
        error_message: Optional[str] = None,
        completion_percentage: float = 0.0,
        task_metadata: Optional[Dict[str, Any]] = None,
        results: Optional[Dict[str, Any]] = None,
        date_started: Optional[datetime] = None,
        date_completed: Optional[datetime] = None,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        super().__init__(id, date_created, date_modified)
        self.video_id = video_id
        self.task_type = task_type
        self.status = status
        self.error_message = error_message
        self.completion_percentage = completion_percentage
        self.task_metadata = task_metadata or {}
        self.results = results or {}
        self.date_started = date_started
        self.date_completed = date_completed