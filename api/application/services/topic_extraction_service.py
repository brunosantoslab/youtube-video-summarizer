# api/application/services/topic_extraction_service.py
import logging
from typing import Optional, List, Dict, Any
import uuid
from datetime import timedelta

from domain.models.topic import Topic
from domain.models.transcript import Transcript, TranscriptSegment
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.summary_repository import ISummaryRepository
from domain.repositories.transcript_repository import ITranscriptRepository
from domain.repositories.topic_repository import ITopicRepository
from infrastructure.external.ai.langchain_client import LangChainClient
from application.events.event_publisher import IEventPublisher
from application.events.topic_events import TopicsExtractedEvent, TopicsExtractionFailedEvent

logger = logging.getLogger(__name__)


class TopicExtractionService:
    """Service for extracting key topics from video summaries and transcripts"""
    
    def __init__(
        self,
        video_repository: IVideoRepository,
        summary_repository: ISummaryRepository,
        transcript_repository: ITranscriptRepository,
        topic_repository: ITopicRepository,
        langchain_client: LangChainClient,
        event_publisher: IEventPublisher
    ):
        self.video_repository = video_repository
        self.summary_repository = summary_repository
        self.transcript_repository = transcript_repository
        self.topic_repository = topic_repository
        self.langchain_client = langchain_client
        self.event_publisher = event_publisher
    
    async def extract_topics(
        self, 
        summary_id: uuid.UUID,
        max_topics: int = 5,
        min_relevance: float = 0.3
    ) -> List[Topic]:
        """
        Extract topics from a summary
        
        Args:
            summary_id: UUID of the summary
            max_topics: Maximum number of topics to extract
            min_relevance: Minimum relevance score (0.0 to 1.0)
            
        Returns:
            List of extracted Topic entities
        """
        # Get summary
        summary = self.summary_repository.get_by_id(summary_id)
        if not summary:
            raise ValueError(f"Summary with ID {summary_id} not found")
        
        try:
            # Extract topics using LangChain
            topics_data = await self.langchain_client.extract_topics(
                text=summary.content,
                max_topics=max_topics,
                min_relevance=min_relevance
            )
            
            # Create Topic entities
            topics = []
            for topic_data in topics_data:
                topic = Topic(
                    video_id=summary.video_id,
                    summary_id=summary_id,
                    name=topic_data["name"],
                    description=topic_data["description"],
                    relevance=topic_data["relevance"]
                )
                topics.append(topic)
            
            # Try to detect timestamps if transcript is available
            transcript = self.transcript_repository.get_by_video_id(summary.video_id)
            if transcript and transcript.segments:
                await self._add_timestamps_to_topics(transcript, topics)
            
            # Save topics to database
            saved_topics = self.topic_repository.create_many(topics)
            
            # Publish event
            await self.event_publisher.publish(
                TopicsExtractedEvent(
                    video_id=str(summary.video_id),
                    summary_id=str(summary_id),
                    topics_count=len(saved_topics)
                )
            )
            
            return saved_topics
            
        except Exception as e:
            logger.error(f"Error extracting topics for summary {summary_id}: {str(e)}")
            
            # Publish failure event
            await self.event_publisher.publish(
                TopicsExtractionFailedEvent(
                    video_id=str(summary.video_id),
                    summary_id=str(summary_id),
                    error=str(e)
                )
            )
            
            raise
    
    async def _add_timestamps_to_topics(self, transcript: Transcript, topics: List[Topic]):
        """
        Attempt to detect when topics appear in the transcript
        
        Args:
            transcript: Transcript entity with segments
            topics: List of Topic entities to update with timestamps
        """
        if not transcript.segments:
            return
        
        # Convert transcript segments to the format expected by the LangChain client
        segments_data = []
        for segment in transcript.segments:
            segments_data.append({
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "text": segment.text
            })
        
        # Convert topics to the format expected by the LangChain client
        topics_data = []
        for topic in topics:
            topics_data.append({
                "name": topic.name,
                "description": topic.description
            })
        
        try:
            # Detect timestamps
            timestamps = await self.langchain_client.detect_topic_timestamps(
                transcript_segments=segments_data,
                topics=topics_data
            )
            
            # Update topic entities with timestamps
            for topic in topics:
                if topic.name in timestamps:
                    timestamp_data = timestamps[topic.name]
                    if timestamp_data["start"] is not None:
                        topic.start_time = timedelta(seconds=timestamp_data["start"])
                    if timestamp_data["end"] is not None:
                        topic.end_time = timedelta(seconds=timestamp_data["end"])
        
        except Exception as e:
            # Just log the error but don't fail the whole process
            logger.warning(f"Error detecting topic timestamps: {str(e)}")
    
    async def rank_topics_by_relevance(self, video_id: uuid.UUID) -> List[Topic]:
        """
        Get topics for a video ranked by relevance
        
        Args:
            video_id: UUID of the video
            
        Returns:
            List of Topic entities ranked by relevance
        """
        topics = self.topic_repository.get_by_video_id(video_id)
        return sorted(topics, key=lambda t: t.relevance, reverse=True)