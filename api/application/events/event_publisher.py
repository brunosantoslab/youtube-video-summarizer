# api/application/events/event_publisher.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

T = TypeVar('T')


class Event(Generic[T]):
    """Base class for all events"""
    
    def __init__(self, event_type: str, payload: T):
        self.event_type = event_type
        self.payload = payload


class IEventPublisher(ABC):
    """Interface for event publishers"""
    
    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event"""
        pass


class VideoDiscoveredEvent(Event[Dict[str, Any]]):
    """Event raised when a new video is discovered"""
    
    def __init__(self, video_id: str):
        super().__init__("video.discovered", {"video_id": str(video_id)})