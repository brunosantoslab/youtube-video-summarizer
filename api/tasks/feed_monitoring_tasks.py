# api/tasks/feed_monitoring_tasks.py
import logging
from typing import List
import uuid

from celery import shared_task

from infrastructure.persistence.database import get_db
from infrastructure.repositories.repository_factory import get_repository_factory
from infrastructure.external.youtube.client import YouTubeApiClient
from infrastructure.events.redis_event_publisher import RedisEventPublisher
from domain.repositories.user_repository import IUserRepository
from domain.repositories.video_repository import IVideoRepository
from application.services.feed_monitoring_service import FeedMonitoringService

logger = logging.getLogger(__name__)


@shared_task
def check_user_feed(user_id: str) -> List[str]:
    """Check a single user's feed for new videos"""
    try:
        # Get dependencies
        session = get_db()
        repository_factory = get_repository_factory(session)
        user_repository = repository_factory.get(IUserRepository)
        video_repository = repository_factory.get(IVideoRepository)
        
        youtube_client = YouTubeApiClient()
        event_publisher = RedisEventPublisher()
        
        # Create service
        service = FeedMonitoringService(
            user_repository=user_repository,
            video_repository=video_repository,
            youtube_client=youtube_client,
            event_publisher=event_publisher
        )
        
        # Execute service method
        new_videos = service.check_for_new_videos(uuid.UUID(user_id))
        
        # Return video IDs
        return [str(video.id) for video in new_videos]
    
    except Exception as e:
        logger.error(f"Error checking feed for user {user_id}: {str(e)}")
        raise
    finally:
        # Close connections
        session.close()
        youtube_client.close()


@shared_task
def check_all_user_feeds():
    """Check all users' feeds for new videos"""
    try:
        # Get all active users
        session = get_db()
        repository_factory = get_repository_factory(session)
        user_repository = repository_factory.get(IUserRepository)
        
        # Get all active users
        users = user_repository.list()
        
        # Schedule individual tasks for each user
        for user in users:
            check_user_feed.delay(str(user.id))
        
        return len(users)
    
    except Exception as e:
        logger.error(f"Error scheduling feed checks: {str(e)}")
        raise