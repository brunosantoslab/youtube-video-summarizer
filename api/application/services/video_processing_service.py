# api/application/services/video_processing_service.py
import logging
from typing import Optional, List, Dict, Any
import uuid

from domain.models.video import VideoStatus
from domain.models.processing import ProcessingTask, ProcessingStatus
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.processing_repository import IProcessingRepository
from application.events.event_publisher import IEventPublisher

logger = logging.getLogger(__name__)


class VideoProcessingService:
    """Service for managing video processing workflows"""
    
    def __init__(
        self,
        video_repository: IVideoRepository,
        processing_repository: IProcessingRepository,
        event_publisher: IEventPublisher,
        task_queue_service
    ):
        self.video_repository = video_repository
        self.processing_repository = processing_repository
        self.event_publisher = event_publisher
        self.task_queue_service = task_queue_service
    
    def queue_video_for_processing(self, video_id: uuid.UUID) -> List[ProcessingTask]:
        """
        Queue a video for all processing steps
        
        Args:
            video_id: UUID of the video to process
            
        Returns:
            List of created processing tasks
        """
        # Get the video
        video = self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")
        
        # Update video status
        video.status = VideoStatus.PROCESSING
        self.video_repository.update(video)
        
        # Create processing tasks for each step
        tasks = []
        
        # 1. Transcript extraction task
        transcript_task = ProcessingTask(
            video_id=video_id,
            task_type="transcript_extraction",
            status=ProcessingStatus.PENDING,
            task_metadata={
                "youtube_id": video.youtube_id
            }
        )
        tasks.append(self.processing_repository.create(transcript_task))
        
        # 2. Summary generation task (depends on transcript)
        summary_task = ProcessingTask(
            video_id=video_id,
            task_type="summary_generation",
            status=ProcessingStatus.PENDING,
            task_metadata={
                "youtube_id": video.youtube_id
            }
        )
        tasks.append(self.processing_repository.create(summary_task))
        
        # 3. Topic extraction task (depends on summary)
        topic_task = ProcessingTask(
            video_id=video_id,
            task_type="topic_extraction",
            status=ProcessingStatus.PENDING,
            task_metadata={
                "youtube_id": video.youtube_id
            }
        )
        tasks.append(self.processing_repository.create(topic_task))
        
        # Queue the first task (transcript extraction)
        self.task_queue_service.enqueue_task(
            "tasks.process_video_step",
            args=[str(video_id), "transcript_extraction"]
        )
        
        return tasks
    
    def handle_step_completion(
        self, 
        video_id: uuid.UUID, 
        task_type: str, 
        success: bool, 
        result_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Handle completion of a processing step
        
        Args:
            video_id: UUID of the video
            task_type: Type of task that completed
            success: Whether the task succeeded
            result_id: ID of the result (e.g., transcript ID, summary ID)
            error: Error message if task failed
        """
        # Find the task for this step
        tasks = self.processing_repository.get_by_video_id(video_id)
        task = next((t for t in tasks if t.task_type == task_type), None)
        
        if not task:
            logger.error(f"No {task_type} task found for video {video_id}")
            return
        
        # Update task status
        status = ProcessingStatus.COMPLETED if success else ProcessingStatus.FAILED
        error_message = error if not success else None
        
        updated_task = self.processing_repository.update_status(
            task_id=task.id,
            status=status,
            error_message=error_message,
            completion_percentage=100.0 if success else 0.0
        )
        
        # Update results if successful
        if success and result_id:
            # Instead of calling update_results which would trigger another update_status call
            # We'll directly update the results value in our updated_task
            updated_task.results = updated_task.results or {}
            updated_task.results["result_id"] = result_id
        
        # If task failed, mark video as failed
        if not success:
            video = self.video_repository.get_by_id(video_id)
            if video:
                video.status = VideoStatus.FAILED
                self.video_repository.update(video)
            return
        
        # Determine which task to run next
        next_task = None
        if task_type == "transcript_extraction":
            next_task = "summary_generation"
        elif task_type == "summary_generation":
            next_task = "topic_extraction"
        elif task_type == "topic_extraction":
            # All tasks complete, mark video as processed
            video = self.video_repository.get_by_id(video_id)
            if video:
                video.status = VideoStatus.PROCESSED
                self.video_repository.update(video)
        
        # Queue the next task if there is one
        if next_task:
            # Find the task for the next step
            next_task_obj = next((t for t in tasks if t.task_type == next_task), None)
            
            if next_task_obj:
                # Instead of updating the task status here, we'll do it after the task is queued
                # Queue the task - pass the result_id as the first parameter for topic_extraction task
                next_args = [result_id, next_task] if next_task == "topic_extraction" else [str(video_id), next_task]
                self.task_queue_service.enqueue_task(
                    "tasks.process_video_step",
                    args=next_args
                )
    
    def get_processing_status(self, video_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get processing status for a video
        
        Args:
            video_id: UUID of the video
            
        Returns:
            Dictionary with processing status information
        """
        # Get all processing tasks for this video
        tasks = self.processing_repository.get_by_video_id(video_id)
        
        # Get video status
        video = self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")
        
        # Calculate overall progress
        total_percentage = sum(task.completion_percentage for task in tasks)
        overall_percentage = total_percentage / len(tasks) if tasks else 0
        
        # Determine overall status
        failed_tasks = [t for t in tasks if t.status == ProcessingStatus.FAILED]
        completed_tasks = [t for t in tasks if t.status == ProcessingStatus.COMPLETED]
        
        if failed_tasks:
            overall_status = "failed"
            error = failed_tasks[0].error_message
        elif len(completed_tasks) == len(tasks):
            overall_status = "completed"
            error = None
        else:
            overall_status = "in_progress"
            error = None
        
        # Build status response
        task_statuses = {}
        for task in tasks:
            task_statuses[task.task_type] = {
                "status": task.status.value,
                "progress": task.completion_percentage,
                "started_at": task.date_started.isoformat() if task.date_started else None,
                "completed_at": task.date_completed.isoformat() if task.date_completed else None,
                "error": task.error_message
            }
        
        return {
            "video_id": str(video_id),
            "status": overall_status,
            "progress": overall_percentage,
            "tasks": task_statuses,
            "error": error
        }