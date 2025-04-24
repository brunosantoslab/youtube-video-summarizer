# api/application/events/topic_events.py
from typing import Dict, Any

from application.events.event_publisher import Event


class TopicsExtractedEvent(Event[Dict[str, Any]]):
    """Event raised when topics have been extracted from a summary"""
    
    def __init__(self, video_id: str, summary_id: str, topics_count: int):
        super().__init__(
            "topics.extracted", 
            {
                "video_id": video_id,
                "summary_id": summary_id,
                "topics_count": topics_count
            }
        )


class TopicsExtractionFailedEvent(Event[Dict[str, Any]]):
    """Event raised when topic extraction has failed"""
    
    def __init__(self, video_id: str, summary_id: str, error: str):
        super().__init__(
            "topics.extraction.failed", 
            {
                "video_id": video_id,
                "summary_id": summary_id,
                "error": error
            }
        )