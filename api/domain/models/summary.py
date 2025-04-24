# api/domain/models/summary.py
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from domain.models.common import Entity


class SummaryMetadata:
    """Value object for summary generation metadata"""
    
    def __init__(
        self,
        processing_time: float = 0.0,
        token_count: int = 0,
        prompt_version: str = "1.0",
        confidence_score: float = 0.0,
        model_parameters: Optional[Dict[str, Any]] = None
    ):
        self.processing_time = processing_time
        self.token_count = token_count
        self.prompt_version = prompt_version
        self.confidence_score = confidence_score
        self.model_parameters = model_parameters or {}
    
    def to_dict(self) -> dict:
        return {
            "processing_time": self.processing_time,
            "token_count": self.token_count,
            "prompt_version": self.prompt_version,
            "confidence_score": self.confidence_score,
            "model_parameters": self.model_parameters
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SummaryMetadata":
        return cls(
            processing_time=data.get("processing_time", 0.0),
            token_count=data.get("token_count", 0),
            prompt_version=data.get("prompt_version", "1.0"),
            confidence_score=data.get("confidence_score", 0.0),
            model_parameters=data.get("model_parameters", {})
        )


class Summary(Entity):
    """Entity representing an AI-generated summary of a video"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        video_id: Optional[uuid.UUID] = None,
        content: str = "",
        model_provider: str = "",
        model_version: str = "",
        processing_metadata: Optional[SummaryMetadata] = None,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        super().__init__(id, date_created, date_modified)
        self.video_id = video_id
        self.content = content
        self.model_provider = model_provider
        self.model_version = model_version
        self.processing_metadata = processing_metadata or SummaryMetadata()