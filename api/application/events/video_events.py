# api/application/events/video_events.py
from typing import Dict, Any

from application.events.event_publisher import Event


class VideoDiscoveredEvent(Event[Dict[str, Any]]):
    """Event raised when a new video is discovered"""
    
    def __init__(self, video_id: str):
        super().__init__(
            "video.discovered", 
            {
                "video_id": video_id
            }
        )


class ProcessingStartedEvent(Event[Dict[str, Any]]):
    """Event raised when video processing begins"""
    
    def __init__(self, video_id: str):
        super().__init__(
            "video.processing.started", 
            {
                "video_id": video_id
            }
        )


class ProcessingCompletedEvent(Event[Dict[str, Any]]):
    """Event raised when video processing completes"""
    
    def __init__(self, video_id: str):
        super().__init__(
            "video.processing.completed", 
            {
                "video_id": video_id
            }
        )


class ProcessingFailedEvent(Event[Dict[str, Any]]):
    """Event raised when video processing fails"""
    
    def __init__(self, video_id: str, error: str):
        super().__init__(
            "video.processing.failed", 
            {
                "video_id": video_id,
                "error": error
            }
        )