# api/tasks/video_processing_tasks.py
import logging
import uuid
from typing import Optional

from celery import shared_task, chain

from infrastructure.persistence.database import get_db
from infrastructure.repositories.repository_factory import get_repository_factory
from infrastructure.queue.task_queue_service import TaskQueueService
from infrastructure.events.redis_event_publisher import RedisEventPublisher
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.processing_repository import IProcessingRepository
from domain.models.video import VideoStatus
from domain.models.processing import ProcessingStatus
from application.services.video_processing_service import VideoProcessingService
from tasks.transcription_tasks import extract_transcript
from tasks.summary_tasks import generate_summary
from tasks.topic_tasks import extract_topics

logger = logging.getLogger(__name__)


@shared_task
def process_video_step(video_id: str, task_type: str) -> Optional[str]:
    """Process a single step in the video processing pipeline"""
    try:
        # Get dependencies
        session = get_db()
        repository_factory = get_repository_factory(session)
        video_repository = repository_factory.get(IVideoRepository)
        processing_repository = repository_factory.get(IProcessingRepository)
        
        event_publisher = RedisEventPublisher()
        task_queue = TaskQueueService()
        
        # Process the specific task
        result_id = None
        error = None
        success = False
        
        try:
            if task_type == "transcript_extraction":
                # Call transcript extraction asynchronously
                result = extract_transcript.delay(video_id)
                result_id = result.id
                success = True
            elif task_type == "summary_generation":
                # Call summary generation asynchronously
                result = generate_summary.delay(video_id)
                result_id = result.id
                success = True
            elif task_type == "topic_extraction":
                # The video_id parameter actually contains the summary_id from previous step
                summary_id = video_id
                result = extract_topics.delay(summary_id)
                result_id = result.id
                success = True
            else:
                error = f"Unknown task type: {task_type}"
                success = False
                
        except Exception as e:
            error = str(e)
            success = False
            logger.error(f"Error processing {task_type} for video {video_id}: {error}")
        
        # Create video processing service
        service = VideoProcessingService(
            video_repository=video_repository,
            processing_repository=processing_repository,
            event_publisher=event_publisher,
            task_queue_service=task_queue
        )
        
        # Handle task completion
        service.handle_step_completion(
            video_id=uuid.UUID(video_id),
            task_type=task_type,
            success=success,
            result_id=result_id,
            error=error
        )
        
        return result_id
    
    except Exception as e:
        logger.error(f"Error in process_video_step for video {video_id}, task {task_type}: {str(e)}")
        raise
    finally:
        # Close connections
        session.close()


@shared_task
def check_pending_videos() -> int:
    """Check for pending videos and start processing them"""
    try:
        # Get dependencies
        session = get_db()
        repository_factory = get_repository_factory(session)
        video_repository = repository_factory.get(IVideoRepository)
        processing_repository = repository_factory.get(IProcessingRepository)
        
        event_publisher = RedisEventPublisher()
        task_queue = TaskQueueService()
        
        # Create video processing service
        service = VideoProcessingService(
            video_repository=video_repository,
            processing_repository=processing_repository,
            event_publisher=event_publisher,
            task_queue_service=task_queue
        )
        
        # Get pending videos
        pending_videos = video_repository.get_by_status(VideoStatus.NEW)
        
        # Queue each video for processing
        for video in pending_videos:
            service.queue_video_for_processing(video.id)
        
        return len(pending_videos)
    
    except Exception as e:
        logger.error(f"Error in check_pending_videos: {str(e)}")
        raise
    finally:
        # Close connections
        session.close()


@shared_task
def retry_failed_tasks() -> int:
    """Retry failed tasks"""
    try:
        # Get dependencies
        session = get_db()
        repository_factory = get_repository_factory(session)
        processing_repository = repository_factory.get(IProcessingRepository)
        
        task_queue = TaskQueueService()
        
        # Get failed transcript extraction tasks
        failed_tasks = processing_repository.get_by_type_and_status(
            task_type="transcript_extraction",
            status=ProcessingStatus.FAILED
        )
        
        # Retry each failed task
        retried_count = 0
        for task in failed_tasks:
            # Reset task status
            processing_repository.update_status(
                task_id=task.id,
                status=ProcessingStatus.PENDING,
                error_message=None,
                completion_percentage=0.0
            )
            
            # Queue the task
            task_queue.enqueue_task(
                "tasks.process_video_step",
                args=[str(task.video_id), task.task_type]
            )
            
            retried_count += 1
        
        return retried_count
    
    except Exception as e:
        logger.error(f"Error in retry_failed_tasks: {str(e)}")
        raise
    finally:
        # Close connections
        session.close()