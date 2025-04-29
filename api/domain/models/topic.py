# api/domain/models/topic.py
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uuid

from domain.models.common import Entity


class Topic(Entity):
    """Entity representing a key topic extracted from a video"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        video_id: Optional[uuid.UUID] = None,
        summary_id: Optional[uuid.UUID] = None,
        name: str = "",
        description: str = "",
        relevance: float = 0.0,
        start_time: Optional[timedelta] = None,
        end_time: Optional[timedelta] = None,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        super().__init__(id, date_created, date_modified)
        self.video_id = video_id
        self.summary_id = summary_id
        self.name = name
        self.description = description
        self.relevance = relevance  # 0.0 to 1.0
        self.start_time = start_time  # Optional timestamp in video
        self.end_time = end_time      # Optional timestamp in video