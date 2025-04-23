# api/application/events/transcript_events.py
from typing import Dict, Any

from application.events.event_publisher import Event


class TranscriptExtractedEvent(Event[Dict[str, Any]]):
    """Event raised when a transcript has been extracted"""
    
    def __init__(self, transcript_id: str, video_id: str):
        super().__init__(
            "transcript.extracted", 
            {
                "transcript_id": transcript_id,
                "video_id": video_id
            }
        )


class TranscriptProcessedEvent(Event[Dict[str, Any]]):
    """Event raised when a transcript has been processed"""
    
    def __init__(self, transcript_id: str, video_id: str):
        super().__init__(
            "transcript.processed", 
            {
                "transcript_id": transcript_id,
                "video_id": video_id
            }
        )