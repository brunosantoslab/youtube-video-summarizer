# api/tasks/transcription_tasks.py
import logging
import uuid
import asyncio
from typing import Optional

from celery import shared_task

from infrastructure.persistence.database import get_db
from infrastructure.repositories.repository_factory import get_repository_factory
from infrastructure.external.youtube.client import YouTubeApiClient
from infrastructure.external.youtube.audio_downloader import YouTubeAudioDownloader
from infrastructure.external.ai.whisper_client import WhisperApiClient
from api.infrastructure.events.redis_event_publisher import RedisEventPublisher
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.transcript_repository import ITranscriptRepository
from application.services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


@shared_task
def extract_transcript(video_id: str) -> Optional[str]:
    """Extract transcript for a video"""
    try:
        # Get dependencies
        session = get_db()
        repository_factory = get_repository_factory(session)
        video_repository = repository_factory.get(IVideoRepository)
        transcript_repository = repository_factory.get(ITranscriptRepository)
        
        youtube_client = YouTubeApiClient()
        audio_downloader = YouTubeAudioDownloader()
        whisper_client = WhisperApiClient()
        event_publisher = RedisEventPublisher()
        
        # Create service
        service = TranscriptionService(
            video_repository=video_repository,
            transcript_repository=transcript_repository,
            youtube_client=youtube_client,
            audio_downloader=audio_downloader,
            whisper_client=whisper_client,
            event_publisher=event_publisher
        )
        
        # Run async method in sync context
        loop = asyncio.get_event_loop()
        transcript = loop.run_until_complete(
            service.extract_transcript(uuid.UUID(video_id))
        )
        
        # Return transcript ID
        return str(transcript.id)
    
    except Exception as e:
        logger.error(f"Error extracting transcript for video {video_id}: {str(e)}")
        raise
    finally:
        # Close connections
        session.close()
        loop.run_until_complete(youtube_client.close())