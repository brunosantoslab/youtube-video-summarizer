# api/tests/unit/repositories/test_user_repository.py
import uuid

from unittest.mock import MagicMock

from domain.models.user import User, UserPreferences
from infrastructure.persistence.user_entity import UserEntity
from infrastructure.repositories.user_repository import PostgresUserRepository


def test_get_by_id():
    # Arrange
    session_mock = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    user_id = uuid.uuid4()
    
    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    
    user_entity = UserEntity(
        id=user_id,
        email="test@example.com",
        youtube_user_id="yt123",
        display_name="Test User",
        preferences_json={"summary_length": "Standard"}
    )
    filter_mock.first.return_value = user_entity
    
    repo = PostgresUserRepository(session_mock)
    
    # Act
    result = repo.get_by_id(user_id)
    
    # Assert
    assert result is not None
    assert result.id == user_id
    assert result.email == "test@example.com"
    assert result.youtube_user_id == "yt123"
    assert result.display_name == "Test User"
    assert result.preference_settings.summary_length == "Standard"
    
    session_mock.query.assert_called_once_with(UserEntity)
    query_mock.filter.assert_called_once()


def test_create_user():
    # Arrange
    session_mock = MagicMock()
    user_id = uuid.uuid4()
    
    user = User(
        id=user_id,
        email="test@example.com",
        youtube_user_id="yt123",
        display_name="Test User",
        preference_settings=UserPreferences(summary_length="Brief")
    )
    
    repo = PostgresUserRepository(session_mock)
    
    # Act
    result = repo.create(user)
    
    # Assert
    assert result.id == user_id
    assert result.email == "test@example.com"
    
    session_mock.add.assert_called_once()
    session_mock.commit.assert_called_once()
    session_mock.refresh.assert_called_once()


def test_update_user():
    # Arrange
    session_mock = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    user_id = uuid.uuid4()
    
    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    
    existing_user_entity = UserEntity(
        id=user_id,
        email="old@example.com",
        youtube_user_id="yt123",
        display_name="Old Name",
        preferences_json={"summary_length": "Standard"}
    )
    filter_mock.first.return_value = existing_user_entity
    
    updated_user = User(
        id=user_id,
        email="new@example.com",
        youtube_user_id="yt123",
        display_name="New Name",
        preference_settings=UserPreferences(summary_length="Detailed")
    )
    
    repo = PostgresUserRepository(session_mock)
    
    # Act
    result = repo.update(updated_user)
    
    # Assert
    assert result.id == user_id
    assert result.email == "new@example.com"
    assert result.display_name == "New Name"
    
    session_mock.query.assert_called_once_with(UserEntity)
    query_mock.filter.assert_called_once()
    session_mock.commit.assert_called_once()
    session_mock.refresh.assert_called_once()


def test_delete_user():
    # Arrange
    session_mock = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    user_id = uuid.uuid4()
    
    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    
    user_entity = UserEntity(
        id=user_id,
        email="test@example.com",
        youtube_user_id="yt123",
        display_name="Test User"
    )
    filter_mock.first.return_value = user_entity
    
    repo = PostgresUserRepository(session_mock)
    
    # Act
    result = repo.delete(user_id)
    
    # Assert
    assert result is True
    
    session_mock.query.assert_called_once_with(UserEntity)
    query_mock.filter.assert_called_once()
    session_mock.delete.assert_called_once_with(user_entity)
    session_mock.commit.assert_called_once()