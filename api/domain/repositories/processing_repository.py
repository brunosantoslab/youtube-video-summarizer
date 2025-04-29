# api/domain/repositories/processing_repository.py
from abc import abstractmethod
from typing import Any, Dict, Optional, List
import uuid

from domain.models.processing import ProcessingTask, ProcessingStatus
from domain.repositories.base_repository import IRepository


class IProcessingRepository(IRepository[ProcessingTask]):
    """Repository interface for ProcessingTask entity"""
    
    @abstractmethod
    def get_by_video_id(self, video_id: uuid.UUID) -> List[ProcessingTask]:
        """Get processing tasks for a video"""
        pass
    
    @abstractmethod
    def get_by_type_and_status(
        self, 
        task_type: str, 
        status: ProcessingStatus,
        limit: int = 100
    ) -> List[ProcessingTask]:
        """Get processing tasks by type and status"""
        pass
    
    @abstractmethod
    def update_status(
        self,
        task_id: uuid.UUID,
        status: ProcessingStatus,
        error_message: Optional[str] = None,
        completion_percentage: Optional[float] = None
    ) -> ProcessingTask:
        """Update the status of a processing task"""
        pass
    
    @abstractmethod
    def update_results(
        self,
        task_id: uuid.UUID,
        results: Dict[str, Any]
    ) -> ProcessingTask:
        """Update the results of a processing task"""
        pass