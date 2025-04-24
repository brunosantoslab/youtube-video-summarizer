# api/tasks/topic_tasks.py
import logging
import uuid
import asyncio
from typing import List

from celery import shared_task

from infrastructure.persistence.database import get_db
from infrastructure.repositories.repository_factory import get_repository_factory
from infrastructure.external.ai.langchain_client import LangChainClient
from infrastructure.events.redis_event_publisher import RedisEventPublisher
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.summary_repository import ISummaryRepository
from domain.repositories.transcript_repository import ITranscriptRepository
from domain.repositories.topic_repository import ITopicRepository
from application.services.topic_extraction_service import TopicExtractionService

logger = logging.getLogger(__name__)


@shared_task
def extract_topics(
    summary_id: str,
    max_topics: int = 5,
    min_relevance: float = 0.3
) -> List[str]:
    """Extract topics from a summary"""
    try:
        # Get dependencies
        session = get_db()
        repository_factory = get_repository_factory(session)
        video_repository = repository_factory.get(IVideoRepository)
        summary_repository = repository_factory.get(ISummaryRepository)
        transcript_repository = repository_factory.get(ITranscriptRepository)
        topic_repository = repository_factory.get(ITopicRepository)
        
        langchain_client = LangChainClient()
        event_publisher = RedisEventPublisher()
        
        # Create service
        service = TopicExtractionService(
            video_repository=video_repository,
            summary_repository=summary_repository,
            transcript_repository=transcript_repository,
            topic_repository=topic_repository,
            langchain_client=langchain_client,
            event_publisher=event_publisher
        )
        
        # Run async method in sync context
        loop = asyncio.get_event_loop()
        topics = loop.run_until_complete(
            service.extract_topics(
                uuid.UUID(summary_id),
                max_topics=max_topics,
                min_relevance=min_relevance
            )
        )
        
        # Return topic IDs
        return [str(topic.id) for topic in topics]
    
    except Exception as e:
        logger.error(f"Error extracting topics for summary {summary_id}: {str(e)}")
        raise
    finally:
        # Close connections
        session.close()