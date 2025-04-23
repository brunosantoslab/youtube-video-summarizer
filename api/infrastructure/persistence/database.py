# api/infrastructure/persistence/database.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config import get_settings


class Database:
    def __init__(self, db_url: str = None):
        self.db_url = db_url or get_settings().database_url
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def create_all(self):
        """Create all tables"""
        from infrastructure.persistence.base import Base
        Base.metadata.create_all(bind=self.engine)


# Singleton instance
db = Database()


def get_db() -> Generator[Session, None, None]:
    """Dependency to get DB session"""
    return next(db.get_session())