"""
Integration tests for User Repository using TestContainers
Author: Bruno Santos
"""
import uuid
import pytest
from sqlalchemy import select

from domain.models.user import User
from infrastructure.persistence.user_entity import UserEntity
from infrastructure.repositories.user_repository import PostgresUserRepository as UserRepository


@pytest.mark.integration
class TestUserRepository:
    """Integration tests for UserRepository"""
    
    @pytest.fixture
    def user_repository(self, db_session):
        """Create a user repository with test database session"""
        return UserRepository(db_session)
    
    def test_create_user(self, user_repository, db_session):
        """Test creating a user in the database"""
        # Create a user object
        user = User(
            email="test@example.com",
            youtube_user_id="youtube123",
            display_name="Test User",
            settings={"theme": "dark"}
        )
        
        # Save the user
        created_user = user_repository.create(user)
        
        # Force flush to the database
        db_session.flush()
        
        # Get the user entity from the database
        stmt = select(UserEntity).where(UserEntity.email == "test@example.com")
        result = db_session.execute(stmt).scalar_one()
        
        # Verify the user was saved correctly
        assert result is not None
        assert result.email == "test@example.com"
        assert result.youtube_user_id == "youtube123"
        assert result.display_name == "Test User"
        assert result.settings == {"theme": "dark"}
        
        # Verify the domain object was updated with ID
        assert created_user.id is not None
        assert isinstance(created_user.id, uuid.UUID)
    
    def test_get_user_by_id(self, user_repository, db_session):
        """Test retrieving a user by ID"""
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email="test2@example.com",
            youtube_user_id="youtube456",
            display_name="Test User 2",
            settings={"theme": "light"}
        )
        db_session.add(user_entity)
        db_session.flush()
        
        # Get the user by ID
        user = user_repository.get_by_id(user_entity.id)
        
        # Verify the user was retrieved correctly
        assert user is not None
        assert user.id == user_entity.id
        assert user.email == "test2@example.com"
        assert user.youtube_user_id == "youtube456"
        assert user.display_name == "Test User 2"
        assert user.settings == {"theme": "light"}
    
    def test_get_user_by_email(self, user_repository, db_session):
        """Test retrieving a user by email"""
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email="test3@example.com",
            youtube_user_id="youtube789",
            display_name="Test User 3"
        )
        db_session.add(user_entity)
        db_session.flush()
        
        # Get the user by email
        user = user_repository.get_by_email("test3@example.com")
        
        # Verify the user was retrieved correctly
        assert user is not None
        assert user.id == user_entity.id
        assert user.email == "test3@example.com"
        assert user.youtube_user_id == "youtube789"
        assert user.display_name == "Test User 3"
    
    def test_update_user(self, user_repository, db_session):
        """Test updating a user"""
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email="test4@example.com",
            youtube_user_id="youtube101",
            display_name="Test User 4",
            settings={"notifications": True}
        )
        db_session.add(user_entity)
        db_session.flush()
        
        # Get the user and update it
        user = user_repository.get_by_id(user_entity.id)
        user.display_name = "Updated Name"
        user.settings = {"notifications": False}
        
        # Update the user
        updated_user = user_repository.update(user)
        db_session.flush()
        
        # Verify the user was updated in the database
        stmt = select(UserEntity).where(UserEntity.id == user_entity.id)
        result = db_session.execute(stmt).scalar_one()
        
        assert result.display_name == "Updated Name"
        assert result.settings == {"notifications": False}
        
        # Verify the returned object is correct
        assert updated_user.display_name == "Updated Name"
        assert updated_user.settings == {"notifications": False}
    
    def test_delete_user(self, user_repository, db_session):
        """Test deleting a user"""
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email="test5@example.com",
            youtube_user_id="youtube102",
            display_name="Test User 5"
        )
        db_session.add(user_entity)
        db_session.flush()
        user_id = user_entity.id
        
        # Delete the user
        result = user_repository.delete(user_id)
        db_session.flush()
        
        # Verify the user was deleted
        assert result is True
        
        # Verify the user is no longer in the database
        stmt = select(UserEntity).where(UserEntity.id == user_id)
        result = db_session.execute(stmt).scalar_one_or_none()
        assert result is None
    
    def test_get_all_users(self, user_repository, db_session):
        """Test retrieving all users"""
        # Create multiple user entities
        users = [
            UserEntity(email="user1@example.com", youtube_user_id="yt1", display_name="User 1"),
            UserEntity(email="user2@example.com", youtube_user_id="yt2", display_name="User 2"),
            UserEntity(email="user3@example.com", youtube_user_id="yt3", display_name="User 3")
        ]
        for user in users:
            db_session.add(user)
        db_session.flush()
        
        # Get all users
        all_users = user_repository.get_all()
        
        # Verify we have at least 3 users (there might be more from other tests)
        assert len(all_users) >= 3
        
        # Verify our newly created users are in the result
        emails = [user.email for user in all_users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
        assert "user3@example.com" in emails
