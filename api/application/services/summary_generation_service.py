# api/application/services/summary_generation_service.py
import logging
from typing import Optional, Dict, Any
import uuid
import time
from datetime import datetime

from domain.models.summary import Summary, SummaryMetadata
from domain.models.transcript import Transcript
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.transcript_repository import ITranscriptRepository
from domain.repositories.summary_repository import ISummaryRepository
from infrastructure.external.ai.ai_provider_client import AIProviderClient
from application.events.event_publisher import IEventPublisher
from application.events.summary_events import SummaryGeneratedEvent, SummaryFailedEvent

logger = logging.getLogger(__name__)


class SummaryGenerationService:
    """Service for generating summaries from video transcripts"""
    
    def __init__(
        self,
        video_repository: IVideoRepository,
        transcript_repository: ITranscriptRepository,
        summary_repository: ISummaryRepository,
        ai_provider_client: AIProviderClient,
        event_publisher: IEventPublisher
    ):
        self.video_repository = video_repository
        self.transcript_repository = transcript_repository
        self.summary_repository = summary_repository
        self.ai_provider_client = ai_provider_client
        self.event_publisher = event_publisher
    
    async def generate_summary(
        self, 
        video_id: uuid.UUID,
        ai_provider: Optional[str] = None,
        max_length: Optional[int] = None
    ) -> Summary:
        """
        Generate a summary for a video
        
        Args:
            video_id: UUID of the video
            ai_provider: AI provider to use (openai, google)
            max_length: Maximum length of summary in tokens
            
        Returns:
            Generated Summary entity
        """
        # Get video
        video = self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")
        
        # Get transcript
        transcript = self.transcript_repository.get_by_video_id(video_id)
        if not transcript:
            raise ValueError(f"No transcript found for video {video_id}")
        
        # Optimize the transcript for summarization
        optimized_transcript = self._optimize_transcript(transcript)
        
        try:
            # Generate summary with AI
            start_time = time.time()
            result = await self.ai_provider_client.generate_summary(
                transcript_text=optimized_transcript,
                provider=ai_provider,
                max_tokens=max_length
            )
            
            # Create summary entity
            summary = Summary(
                video_id=video_id,
                content=result["text"],
                model_provider=result.get("model", "").split("-")[0],  # Extract provider name
                model_version=result.get("model", "unknown"),
                processing_metadata=SummaryMetadata(
                    processing_time=time.time() - start_time,
                    token_count=result.get("metadata", {}).get("token_count", 0),
                    prompt_version=result.get("metadata", {}).get("prompt_version", "1.0"),
                    confidence_score=0.9,  # Default value
                    model_parameters=result.get("metadata", {}).get("model_parameters", {})
                )
            )
            
            # Save summary
            saved_summary = self.summary_repository.create(summary)
            
            # Publish event
            await self.event_publisher.publish(
                SummaryGeneratedEvent(
                    summary_id=str(saved_summary.id),
                    video_id=str(video_id)
                )
            )
            
            return saved_summary
            
        except Exception as e:
            logger.error(f"Error generating summary for video {video_id}: {str(e)}")
            
            # Publish failure event
            await self.event_publisher.publish(
                SummaryFailedEvent(
                    video_id=str(video_id),
                    error=str(e)
                )
            )
            
            raise
    
    def _optimize_transcript(self, transcript: Transcript) -> str:
        """
        Optimize transcript for summarization
        
        Args:
            transcript: Transcript entity
            
        Returns:
            Optimized transcript text
        """
        # If transcript has segments, use them for better context
        if transcript.segments:
            # Filter out non-speech segments like [MUSIC] or [APPLAUSE]
            segments = []
            for segment in transcript.segments:
                text = segment.text
                if not (text.startswith('[') and text.endswith(']')):
                    segments.append(text)
            
            # Join segments into coherent text
            return " ".join(segments)
        
        # Otherwise use the full content
        return transcript.content
    
    async def get_or_generate_summary(self, video_id: uuid.UUID) -> Summary:
        """
        Get existing summary or generate a new one
        
        Args:
            video_id: UUID of the video
            
        Returns:
            Summary entity
        """
        # Check for existing summary
        existing_summary = self.summary_repository.get_latest_by_video_id(video_id)
        if existing_summary:
            return existing_summary
        
        # Generate new summary
        return await self.generate_summary(video_id)