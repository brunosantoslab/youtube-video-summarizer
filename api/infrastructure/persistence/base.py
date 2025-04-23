# api/infrastructure/persistence/base.py
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class BaseEntity:
    """Base class for all SQLAlchemy entities"""
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = Column(DateTime, default=func.now())
    date_modified = Column(DateTime, default=func.now(), onupdate=func.now())