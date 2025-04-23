# api/infrastructure/events/redis_event_publisher.py
import json
import logging
from typing import Optional

import redis.asyncio as redis

from application.events.event_publisher import IEventPublisher, Event
from config import get_settings

logger = logging.getLogger(__name__)


class RedisEventPublisher(IEventPublisher):
    """Redis implementation of event publisher"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or get_settings().redis_url
        self.redis_client = redis.from_url(self.redis_url)
    
    async def publish(self, event: Event) -> None:
        """Publish an event to Redis pub/sub"""
        try:
            channel = f"events:{event.event_type}"
            payload = {
                "event_type": event.event_type,
                "payload": event.payload
            }
            
            await self.redis_client.publish(channel, json.dumps(payload))
            logger.debug(f"Published event {event.event_type} to Redis")
        except Exception as e:
            logger.error(f"Error publishing event {event.event_type}: {str(e)}")
            raise