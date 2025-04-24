# api/tasks/summary_tasks.py
import logging
import uuid
import asyncio
from typing import Optional

from celery import shared_task

from infrastructure.persistence.database import get_db
from infrastructure.repositories.repository_factory import get_repository_factory
from infrastructure.external.ai.ai_provider_client import AIProviderClient
from infrastructure.caching.redis_cache import RedisCache
from infrastructure.events.redis_event_publisher import RedisEventPublisher
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.transcript_repository import ITranscriptRepository
from domain.repositories.summary_repository import ISummaryRepository
from application.services.summary_generation_service import SummaryGenerationService

logger = logging.getLogger(__name__)


@shared_task
def generate_summary(
    video_id: str,
    ai_provider: Optional[str] = None,
    max_length: Optional[int] = None
) -> Optional[str]:
    """Generate summary for a video"""
    try:
        # Get dependencies
        session = get_db()
        repository_factory = get_repository_factory(session)
        video_repository = repository_factory.get(IVideoRepository)
        transcript_repository = repository_factory.get(ITranscriptRepository)
        summary_repository = repository_factory.get(ISummaryRepository)
        
        redis_cache = RedisCache()
        ai_provider_client = AIProviderClient(redis_cache=redis_cache)
        event_publisher = RedisEventPublisher()
        
        # Create service
        service = SummaryGenerationService(
            video_repository=video_repository,
            transcript_repository=transcript_repository,
            summary_repository=summary_repository,
            ai_provider_client=ai_provider_client,
            event_publisher=event_publisher
        )
        
        # Run async method in sync context
        loop = asyncio.get_event_loop()
        summary = loop.run_until_complete(
            service.generate_summary(
                uuid.UUID(video_id),
                ai_provider=ai_provider,
                max_length=max_length
            )
        )
        
        # Return summary ID
        return str(summary.id)
    
    except Exception as e:
        logger.error(f"Error generating summary for video {video_id}: {str(e)}")
        raise
    finally:
        # Close connections
        session.close()