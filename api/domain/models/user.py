# api/domain/models/user.py
from datetime import datetime
from typing import Optional
import uuid

from domain.models.common import Entity


class UserPreferences:
    """Value object for user preferences"""
    
    def __init__(
        self,
        summary_length: str = "Standard",  # Brief, Standard, Detailed
        topic_highlight_count: int = 5,
        default_language: str = "en",
        email_notifications: bool = False,
        notebook_integration_enabled: bool = True
    ):
        self.summary_length = summary_length
        self.topic_highlight_count = topic_highlight_count
        self.default_language = default_language
        self.email_notifications = email_notifications
        self.notebook_integration_enabled = notebook_integration_enabled
    
    def to_dict(self) -> dict:
        return {
            "summary_length": self.summary_length,
            "topic_highlight_count": self.topic_highlight_count,
            "default_language": self.default_language,
            "email_notifications": self.email_notifications,
            "notebook_integration_enabled": self.notebook_integration_enabled
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        return cls(
            summary_length=data.get("summary_length", "Standard"),
            topic_highlight_count=data.get("topic_highlight_count", 5),
            default_language=data.get("default_language", "en"),
            email_notifications=data.get("email_notifications", False),
            notebook_integration_enabled=data.get("notebook_integration_enabled", True)
        )


class User(Entity):
    """User entity representing a system user"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        email: str = "",
        youtube_user_id: str = "",
        display_name: str = "",
        preference_settings: Optional[UserPreferences] = None,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        super().__init__(id, date_created, date_modified)
        self.email = email
        self.youtube_user_id = youtube_user_id
        self.display_name = display_name
        self.preference_settings = preference_settings or UserPreferences()