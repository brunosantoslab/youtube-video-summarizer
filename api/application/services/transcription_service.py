# api/application/services/transcription_service.py
import logging
from typing import List, Tuple
import uuid

from domain.models.transcript import (
    Transcript, TranscriptSourceType, ProcessingStatus, 
    TranscriptSegment, TranscriptMetadata
)
from domain.models.video import Video, VideoStatus
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.transcript_repository import ITranscriptRepository
from infrastructure.external.youtube.client import YouTubeApiClient
from infrastructure.external.youtube.audio_downloader import YouTubeAudioDownloader
from infrastructure.external.ai.whisper_client import WhisperApiClient
from application.events.event_publisher import IEventPublisher
from application.events.transcript_events import TranscriptExtractedEvent

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for extracting and processing video transcripts"""
    
    def __init__(
        self,
        video_repository: IVideoRepository,
        transcript_repository: ITranscriptRepository,
        youtube_client: YouTubeApiClient,
        audio_downloader: YouTubeAudioDownloader,
        whisper_client: WhisperApiClient,
        event_publisher: IEventPublisher
    ):
        self.video_repository = video_repository
        self.transcript_repository = transcript_repository
        self.youtube_client = youtube_client
        self.audio_downloader = audio_downloader
        self.whisper_client = whisper_client
        self.event_publisher = event_publisher
    
    async def extract_transcript(self, video_id: uuid.UUID) -> Transcript:
        """
        Extract transcript for a video, trying YouTube captions first,
        then falling back to Whisper API
        
        Args:
            video_id: UUID of the video in our database
            
        Returns:
            Transcript entity
        """
        # Get the video
        video = self.video_repository.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")
        
        # Check if transcript already exists
        existing_transcript = self.transcript_repository.get_by_video_id(video_id)
        if existing_transcript and existing_transcript.processing_status != ProcessingStatus.FAILED:
            return existing_transcript
        
        # Create new transcript if needed
        transcript = existing_transcript or Transcript(
            video_id=video_id,
            processing_status=ProcessingStatus.IN_PROGRESS
        )
        
        # Try to get transcript from YouTube
        try:
            youtube_captions = await self.youtube_client.get_video_captions(video.youtube_id)
            
            if youtube_captions:
                logger.info(f"Using YouTube captions for video {video.youtube_id}")
                
                # Parse captions into segments (simplified)
                segments = self._parse_youtube_captions(youtube_captions)
                
                # Update transcript
                transcript.content = " ".join(segment.text for segment in segments)
                transcript.segments = segments
                transcript.source_type = TranscriptSourceType.YOUTUBE
                transcript.processing_status = ProcessingStatus.COMPLETED
                transcript.metadata = TranscriptMetadata(
                    completion_percentage=100.0,
                    processing_time=0.0,  # Not measured for YouTube captions
                    confidence_score=1.0  # Assuming perfect confidence for YouTube captions
                )
                
                # Save and return
                if existing_transcript:
                    updated_transcript = self.transcript_repository.update(transcript)
                else:
                    updated_transcript = self.transcript_repository.create(transcript)
                
                # Publish event
                await self.event_publisher.publish(
                    TranscriptExtractedEvent(
                        transcript_id=str(updated_transcript.id),
                        video_id=str(video_id)
                    )
                )
                
                return updated_transcript
        except Exception as e:
            logger.warning(f"Error getting YouTube captions: {str(e)}, falling back to Whisper")
        
        # Fallback to Whisper API
        try:
            logger.info(f"Using Whisper API for video {video.youtube_id}")
            
            # Download audio
            audio_data, audio_format = self.audio_downloader.download_audio(video.youtube_id)
            
            # Transcribe with Whisper
            whisper_result = await self.whisper_client.transcribe_audio(
                audio_data,
                filename=f"{video.youtube_id}.{audio_format}",
                language=transcript.language_code
            )
            
            # Parse segments
            segments = self.whisper_client.parse_segments(whisper_result)
            
            # Update transcript
            transcript.content = whisper_result.get("text", "")
            transcript.segments = segments
            transcript.source_type = TranscriptSourceType.WHISPER
            transcript.processing_status = ProcessingStatus.COMPLETED
            
            # Extract metadata
            metadata = TranscriptMetadata(
                completion_percentage=100.0,
                processing_time=whisper_result.get("_metadata", {}).get("processing_time", 0.0),
                confidence_score=0.9  # Placeholder, Whisper doesn't provide confidence scores
            )
            transcript.metadata = metadata
            
            # Save and return
            if existing_transcript:
                updated_transcript = self.transcript_repository.update(transcript)
            else:
                updated_transcript = self.transcript_repository.create(transcript)
            
            # Publish event
            await self.event_publisher.publish(
                TranscriptExtractedEvent(
                    transcript_id=str(updated_transcript.id),
                    video_id=str(video_id)
                )
            )
            
            return updated_transcript
            
        except Exception as e:
            logger.error(f"Error transcribing with Whisper: {str(e)}")
            
            # Update transcript with error
            transcript.processing_status = ProcessingStatus.FAILED
            transcript.metadata = TranscriptMetadata(
                completion_percentage=0.0,
                error_message=str(e)
            )
            
            if existing_transcript:
                self.transcript_repository.update(transcript)
            else:
                self.transcript_repository.create(transcript)
            
            raise
    
    def _parse_youtube_captions(self, captions_text: str) -> List[TranscriptSegment]:
        """
        Parse YouTube captions in SRT format to TranscriptSegment objects
        
        Args:
            captions_text: Captions in SRT format
            
        Returns:
            List of TranscriptSegment objects
        """
        segments = []
        lines = captions_text.strip().split("\n")
        
        i = 0
        while i < len(lines):
            # Skip index line
            i += 1
            if i >= len(lines):
                break
            
            # Parse timestamp line
            timestamp_line = lines[i]
            i += 1
            if "-->" not in timestamp_line or i >= len(lines):
                continue
            
            start_time, end_time = self._parse_srt_timestamp(timestamp_line)
            
            # Parse text (can be multiple lines)
            text_lines = []
            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i])
                i += 1
            
            # Skip empty line
            i += 1
            
            # Create segment
            segment = TranscriptSegment(
                start_time=start_time,
                end_time=end_time,
                text=" ".join(text_lines)
            )
            segments.append(segment)
        
        return segments
    
    def _parse_srt_timestamp(self, timestamp_line: str) -> Tuple[float, float]:
        """
        Parse SRT timestamp line to start and end times in seconds
        
        Args:
            timestamp_line: SRT timestamp line (HH:MM:SS,mmm --> HH:MM:SS,mmm)
            
        Returns:
            Tuple of (start_time_seconds, end_time_seconds)
        """
        parts = timestamp_line.split(" --> ")
        if len(parts) != 2:
            raise ValueError(f"Invalid timestamp line: {timestamp_line}")
        
        start_str, end_str = parts
        
        def parse_time(time_str):
            # Format: HH:MM:SS,mmm
            hours, minutes, seconds = time_str.replace(",", ".").split(":")
            return (
                int(hours) * 3600 + 
                int(minutes) * 60 + 
                float(seconds)
            )
        
        return parse_time(start_str), parse_time(end_str)