# api/infrastructure/repositories/repository_factory.py
from typing import Dict, Type, TypeVar, Optional, Any
from sqlalchemy.orm import Session

from domain.repositories.base_repository import IRepository
from domain.repositories.user_repository import IUserRepository
from domain.repositories.video_repository import IVideoRepository
from domain.repositories.transcript_repository import ITranscriptRepository
from domain.repositories.auth import IOAuthTokenRepository
from infrastructure.repositories.user_repository import PostgresUserRepository
from infrastructure.repositories.video_repository import PostgresVideoRepository
from infrastructure.repositories.transcript_repository import PostgresTranscriptRepository
from domain.repositories.summary_repository import ISummaryRepository
from infrastructure.repositories.summary_repository import PostgresSummaryRepository
from domain.repositories.topic_repository import ITopicRepository
from infrastructure.repositories.topic_repository import PostgresTopicRepository
from domain.repositories.processing_repository import IProcessingRepository
from infrastructure.repositories.processing_repository import PostgresProcessingRepository
from infrastructure.repositories.auth import PostgresOAuthTokenRepository


class RepositoryFactory:
    """Factory for creating repository instances"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repositories: Dict[Type[IRepository], Type[Any]] = {
            IUserRepository: PostgresUserRepository,
            IVideoRepository: PostgresVideoRepository,
            ITranscriptRepository: PostgresTranscriptRepository,
            ISummaryRepository: PostgresSummaryRepository,
            ITopicRepository: PostgresTopicRepository,
            IProcessingRepository: PostgresProcessingRepository,
            IOAuthTokenRepository: PostgresOAuthTokenRepository,  # Added OAuth token repository
        }
        self._instances: Dict[Type[IRepository], IRepository] = {}
    
    def get(self, repository_type: Type[IRepository]) -> IRepository:
        """Get a repository instance by its interface type"""
        if repository_type not in self._instances:
            if repository_type not in self.repositories:
                raise ValueError(f"No implementation found for repository type {repository_type.__name__}")
            
            repository_class = self.repositories[repository_type]
            self._instances[repository_type] = repository_class(self.session)
        
        return self._instances[repository_type]


def get_repository_factory(session: Session) -> RepositoryFactory:
    """Create a repository factory for the given session"""
    return RepositoryFactory(session)