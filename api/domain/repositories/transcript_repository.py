# api/domain/repositories/transcript_repository.py
from abc import abstractmethod
from typing import Optional, List
import uuid

from domain.models.transcript import Transcript, ProcessingStatus
from domain.repositories.base_repository import IRepository


class ITranscriptRepository(IRepository[Transcript]):
    """Repository interface for Transcript entity"""
    
    @abstractmethod
    def get_by_video_id(self, video_id: uuid.UUID) -> Optional[Transcript]:
        """Get a transcript by video ID"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: ProcessingStatus, limit: int = 100) -> List[Transcript]:
        """Get transcripts by processing status"""
        pass