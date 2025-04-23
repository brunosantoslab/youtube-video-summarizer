# api/infrastructure/queue/celery_app.py
from celery import Celery
from celery.schedules import crontab

from config import get_settings

# Create Celery instance
celery_app = Celery(
    "youtube_summarizer",
    broker=get_settings().redis_url,
    backend=get_settings().redis_url
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "check-new-videos-every-hour": {
        "task": "tasks.feed_monitoring_tasks.check_all_user_feeds",
        "schedule": crontab(minute=0, hour="*/1"),  # Every hour
    },
}

celery_app.conf.timezone = "UTC"