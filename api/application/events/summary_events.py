# api/application/events/summary_events.py
from typing import Dict, Any

from application.events.event_publisher import Event


class SummaryGeneratedEvent(Event[Dict[str, Any]]):
    """Event raised when a summary has been generated"""
    
    def __init__(self, summary_id: str, video_id: str):
        super().__init__(
            "summary.generated", 
            {
                "summary_id": summary_id,
                "video_id": video_id
            }
        )


class SummaryFailedEvent(Event[Dict[str, Any]]):
    """Event raised when summary generation has failed"""
    
    def __init__(self, video_id: str, error: str):
        super().__init__(
            "summary.failed", 
            {
                "video_id": video_id,
                "error": error
            }
        )