# api/domain/models/transcript.py
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
import uuid

from domain.models.common import Entity


class TranscriptSourceType(Enum):
    YOUTUBE = "youtube"
    WHISPER = "whisper"
    MANUAL = "manual"


class ProcessingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptSegment:
    """Value object representing a time-stamped segment of transcript"""
    
    def __init__(
        self,
        start_time: float,  # seconds
        end_time: float,    # seconds
        text: str
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
    
    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "text": self.text
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TranscriptSegment":
        return cls(
            start_time=data["start_time"],
            end_time=data["end_time"],
            text=data["text"]
        )


class TranscriptMetadata:
    """Value object for transcript processing metadata"""
    
    def __init__(
        self,
        completion_percentage: float = 0.0,
        error_message: Optional[str] = None,
        processing_time: Optional[float] = None,
        confidence_score: Optional[float] = None
    ):
        self.completion_percentage = completion_percentage
        self.error_message = error_message
        self.processing_time = processing_time
        self.confidence_score = confidence_score
    
    def to_dict(self) -> dict:
        return {
            "completion_percentage": self.completion_percentage,
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TranscriptMetadata":
        return cls(
            completion_percentage=data.get("completion_percentage", 0.0),
            error_message=data.get("error_message"),
            processing_time=data.get("processing_time"),
            confidence_score=data.get("confidence_score")
        )


class Transcript(Entity):
    """Entity representing a video transcript"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        video_id: Optional[uuid.UUID] = None,
        content: str = "",
        segments: Optional[List[TranscriptSegment]] = None,
        source_type: TranscriptSourceType = TranscriptSourceType.YOUTUBE,
        language_code: str = "en",
        processing_status: ProcessingStatus = ProcessingStatus.PENDING,
        metadata: Optional[TranscriptMetadata] = None,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        super().__init__(id, date_created, date_modified)
        self.video_id = video_id
        self.content = content
        self.segments = segments or []
        self.source_type = source_type
        self.language_code = language_code
        self.processing_status = processing_status
        self.metadata = metadata or TranscriptMetadata()
    
    def get_full_text(self) -> str:
        """Get the combined text from all segments or the content field"""
        if not self.segments:
            return self.content
        
        return " ".join(segment.text for segment in self.segments)
    
    def update_status(
        self, 
        status: ProcessingStatus, 
        error_message: Optional[str] = None,
        completion_percentage: Optional[float] = None
    ) -> None:
        """Update the processing status and metadata"""
        self.processing_status = status
        
        if error_message is not None:
            self.metadata.error_message = error_message
        
        if completion_percentage is not None:
            self.metadata.completion_percentage = completion_percentage