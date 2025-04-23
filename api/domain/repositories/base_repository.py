# api/domain/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
import uuid

from domain.models.common import Entity

T = TypeVar('T', bound=Entity)


class IRepository(Generic[T], ABC):
    """Base repository interface for all entities"""
    
    @abstractmethod
    def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        """Get an entity by its ID"""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    def delete(self, id: uuid.UUID) -> bool:
        """Delete an entity by its ID"""
        pass
    
    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100) -> List[T]:
        """List entities with optional filtering and pagination"""
        pass