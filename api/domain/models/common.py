# api/domain/models/common.py
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class Entity:
    """Base class for all domain entities"""
    
    def __init__(
        self,
        id: Optional[uuid.UUID] = None,
        date_created: Optional[datetime] = None,
        date_modified: Optional[datetime] = None
    ):
        self.id = id or uuid.uuid4()
        self.date_created = date_created or datetime.utcnow()
        self.date_modified = date_modified or datetime.utcnow()
    
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id


class ValueObject:
    """Base class for all value objects"""
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__