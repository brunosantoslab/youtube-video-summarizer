"""
Integration tests for User Repository using TestContainers
Author: Bruno Santos
"""
import uuid
import pytest
from sqlalchemy import select

from domain.models.user import User, UserPreferences
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
        # Generate unique values for the test
        unique_id = uuid.uuid4().hex
        email = f"test_{unique_id}@example.com"
        youtube_id = f"youtube_{unique_id}"
        
        # Create a user object
        user = User(
            email=email,
            youtube_user_id=youtube_id,
            display_name="Test User",
            preference_settings=UserPreferences(
                summary_length="Detailed",
                default_language="en",
                email_notifications=True,
                notebook_integration_enabled=True
            )
        )
        
        # Save the user
        created_user = user_repository.create(user)
        
        # Force flush to the database
        db_session.flush()
        
        # Get the user entity from the database
        stmt = select(UserEntity).where(UserEntity.email == email)
        result = db_session.execute(stmt).scalar_one()
        
        # Verify the user was saved correctly
        assert result is not None
        assert result.email == email
        assert result.youtube_user_id == youtube_id
        assert result.display_name == "Test User"
        assert result.settings["summary_length"] == "Detailed"
        assert result.settings["email_notifications"] == True
        assert result.settings["notebook_integration_enabled"] == True
        
        # Verify the domain object was updated with ID
        assert created_user.id is not None
        assert isinstance(created_user.id, uuid.UUID)
    
    def test_get_user_by_id(self, user_repository, db_session):
        """Test retrieving a user by ID"""
        # Generate unique values for the test
        unique_id = uuid.uuid4().hex
        email = f"test2_{unique_id}@example.com"
        youtube_id = f"youtube_{unique_id}"
        
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email=email,
            youtube_user_id=youtube_id,
            display_name="Test User 2",
            settings={"summary_length": "Brief", "default_language": "fr"}
        )
        db_session.add(user_entity)
        db_session.flush()
        
        # Get the user by ID
        user = user_repository.get_by_id(user_entity.id)
        
        # Verify the user was retrieved correctly
        assert user is not None
        assert user.id == user_entity.id
        assert user.email == email
        assert user.youtube_user_id == youtube_id
        assert user.display_name == "Test User 2"
        assert user.preference_settings.summary_length == "Brief"
        assert user.preference_settings.default_language == "fr"
    
    def test_get_user_by_email(self, user_repository, db_session):
        """Test retrieving a user by email"""
        # Generate unique values for the test
        unique_id = uuid.uuid4().hex
        email = f"test3_{unique_id}@example.com"
        youtube_id = f"youtube_{unique_id}"
        
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email=email,
            youtube_user_id=youtube_id,
            display_name="Test User 3"
        )
        db_session.add(user_entity)
        db_session.flush()
        
        # Get the user by email
        user = user_repository.get_by_email(email)
        
        # Verify the user was retrieved correctly
        assert user is not None
        assert user.id == user_entity.id
        assert user.email == email
        assert user.youtube_user_id == youtube_id
        assert user.display_name == "Test User 3"
    
    def test_update_user(self, user_repository, db_session):
        """Test updating a user"""
        # Generate unique values for the test
        unique_id = uuid.uuid4().hex
        email = f"test4_{unique_id}@example.com"
        youtube_id = f"youtube_{unique_id}"
        
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email=email,
            youtube_user_id=youtube_id,
            display_name="Test User 4",
            settings={"notifications": True}
        )
        db_session.add(user_entity)
        db_session.flush()
        
        # Get the user and update it
        user = user_repository.get_by_id(user_entity.id)
        user.display_name = "Updated Name"
        user.preference_settings = UserPreferences(
            summary_length="Brief",
            email_notifications=False
        )
        
        # Update the user
        updated_user = user_repository.update(user)
        db_session.flush()
        
        # Verify the user was updated in the database
        stmt = select(UserEntity).where(UserEntity.id == user_entity.id)
        result = db_session.execute(stmt).scalar_one()
        
        assert result.display_name == "Updated Name"
        assert result.settings["summary_length"] == "Brief"
        assert result.settings["email_notifications"] == False
        
        # Verify the returned object is correct
        assert updated_user.display_name == "Updated Name"
        assert updated_user.preference_settings.summary_length == "Brief"
        assert updated_user.preference_settings.email_notifications == False
    
    def test_delete_user(self, user_repository, db_session):
        """Test deleting a user"""
        # Generate unique values for the test
        unique_id = uuid.uuid4().hex
        email = f"test5_{unique_id}@example.com"
        youtube_id = f"youtube_{unique_id}"
        
        # Create a user entity directly in the database
        user_entity = UserEntity(
            email=email,
            youtube_user_id=youtube_id,
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
        # Generate unique values for the test
        unique_id = uuid.uuid4().hex
        
        # Create multiple user entities
        users = [
            UserEntity(email=f"user1_{unique_id}@example.com", youtube_user_id=f"yt1_{unique_id}", display_name="User 1"),
            UserEntity(email=f"user2_{unique_id}@example.com", youtube_user_id=f"yt2_{unique_id}", display_name="User 2"),
            UserEntity(email=f"user3_{unique_id}@example.com", youtube_user_id=f"yt3_{unique_id}", display_name="User 3")
        ]
        for user in users:
            db_session.add(user)
        db_session.flush()
        
        # Get all users
        all_users = user_repository.get_all()
        
        # Verify we have at least 3 users (there might be more from other tests)
        assert len(all_users) >= 3
        
        # Verify our newly created users are in the result
        all_emails = [user.email for user in all_users]
        test_emails = [user.email for user in users]
        
        for email in test_emails:
            assert email in all_emails
