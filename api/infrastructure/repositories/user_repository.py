# api/infrastructure/repositories/user_repository.py
from typing import Optional

from sqlalchemy.orm import Session

from domain.models.user import User
from domain.repositories.user_repository import IUserRepository
from infrastructure.persistence.user_entity import UserEntity
from infrastructure.repositories.base_repository import SQLAlchemyRepository


class PostgresUserRepository(SQLAlchemyRepository[User, UserEntity], IUserRepository):
    """PostgreSQL implementation of User repository"""
    
    def __init__(self, session: Session):
        super().__init__(session, UserEntity)
    
    def get_by_youtube_id(self, youtube_id: str) -> Optional[User]:
        entity = self.session.query(UserEntity).filter(UserEntity.youtube_id == youtube_id).first()
        return entity.to_domain() if entity else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        entity = self.session.query(UserEntity).filter(UserEntity.email == email).first()
        return entity.to_domain() if entity else None