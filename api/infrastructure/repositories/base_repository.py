# api/infrastructure/repositories/base_repository.py
from typing import Generic, TypeVar, Optional, List, Dict, Any
import uuid

from sqlalchemy.orm import Session

from domain.models.common import Entity
from domain.repositories.base_repository import IRepository
from infrastructure.persistence.base import Base, BaseEntity

T = TypeVar('T', bound=Entity)
E = TypeVar('E', bound=BaseEntity)


class SQLAlchemyRepository(Generic[T, E], IRepository[T]):
    """Base SQLAlchemy implementation of repository pattern"""
    
    def __init__(self, session: Session, entity_class: type[E]):
        self.session = session
        self.entity_class = entity_class
    
    def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        entity = self.session.query(self.entity_class).filter(self.entity_class.id == id).first()
        return entity.to_domain() if entity else None
    
    def create(self, domain_entity: T) -> T:
        entity = self.entity_class.from_domain(domain_entity)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity.to_domain()
    
    def update(self, domain_entity: T) -> T:
        entity = self.session.query(self.entity_class).filter(
            self.entity_class.id == domain_entity.id
        ).first()
        
        if not entity:
            raise ValueError(f"Entity with id {domain_entity.id} not found")
        
        # Update the entity with the domain entity values
        updated_entity = self.entity_class.from_domain(domain_entity)
        for key, value in updated_entity.__dict__.items():
            if not key.startswith('_') and key != 'id':
                setattr(entity, key, value)
        
        self.session.commit()
        self.session.refresh(entity)
        return entity.to_domain()
    
    def delete(self, id: uuid.UUID) -> bool:
        entity = self.session.query(self.entity_class).filter(self.entity_class.id == id).first()
        if not entity:
            return False
        
        self.session.delete(entity)
        self.session.commit()
        return True
    
    def list(self, filters: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100) -> List[T]:
        query = self.session.query(self.entity_class)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.entity_class, key):
                    query = query.filter(getattr(self.entity_class, key) == value)
        
        entities = query.offset(skip).limit(limit).all()
        return [entity.to_domain() for entity in entities]