# api/domain/models/saved_summary.py
from datetime import datetime
from typing import Optional
import uuid

from domain.models.common import Entity


class SavedSummary(Entity):
    """Entity representing a summary saved by a user"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        summary_id: Optional[uuid.UUID] = None,
        notes: str = "",
        folder_name: str = "",
        date_saved: Optional[datetime] = None,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        super().__init__(id, date_created, date_modified)
        self.user_id = user_id
        self.summary_id = summary_id
        self.notes = notes
        self.folder_name = folder_name
        self.date_saved = date_saved or datetime.now()