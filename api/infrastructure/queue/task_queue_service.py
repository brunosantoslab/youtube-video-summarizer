# api/infrastructure/queue/task_queue_service.py
import logging
from typing import Optional, List, Dict, Any

from celery import Celery
from celery.schedules import crontab

from config import get_settings

logger = logging.getLogger(__name__)


class TaskQueueService:
    """Service for managing asynchronous tasks"""
    
    def __init__(self, app_name: str = "yvs", broker_url: Optional[str] = None, backend_url: Optional[str] = None):
        self.broker_url = broker_url or get_settings().redis_url
        self.backend_url = backend_url or get_settings().redis_url
        self.app = Celery(app_name, broker=self.broker_url, backend=self.backend_url)
        
        # Configure Celery
        self.app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            worker_max_tasks_per_child=1000,
            broker_connection_retry_on_startup=True
        )
        
        # Configure periodic tasks
        self.app.conf.beat_schedule = {
            'check-pending-videos-every-5-minutes': {
                'task': 'tasks.check_pending_videos',
                'schedule': crontab(minute='*/5'),
            },
            'retry-failed-tasks-every-hour': {
                'task': 'tasks.retry_failed_tasks',
                'schedule': crontab(minute=0, hour='*/1'),
            },
        }
    
    def enqueue_task(
        self, 
        task_name: str, 
        args: Optional[List] = None, 
        kwargs: Optional[Dict[str, Any]] = None,
        countdown: Optional[int] = None
    ) -> str:
        """
        Enqueue a task to be executed asynchronously
        
        Args:
            task_name: Name of the task
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task
            countdown: Delay in seconds before executing the task
            
        Returns:
            Task ID
        """
        args = args or []
        kwargs = kwargs or {}
        
        # Send the task to Celery
        result = self.app.send_task(
            task_name,
            args=args,
            kwargs=kwargs,
            countdown=countdown
        )
        
        logger.debug(f"Enqueued task {task_name} with ID {result.id}")
        return result.id
    
    def get_task_result(self, task_id: str) -> Any:
        """
        Get the result of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task result
        """
        result = self.app.AsyncResult(task_id)
        
        if result.ready():
            if result.successful():
                return result.get()
            else:
                raise result.get(propagate=False)
        
        return None
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dictionary with task status information
        """
        result = self.app.AsyncResult(task_id)
        
        status = {
            "id": task_id,
            "status": result.status,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
            "result": result.get() if result.ready() and result.successful() else None,
            "error": str(result.get(propagate=False)) if result.ready() and not result.successful() else None
        }
        
        return status