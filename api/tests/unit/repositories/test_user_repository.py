# api/tests/unit/repositories/test_user_repository.py
import uuid

from unittest.mock import MagicMock, patch

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
    
    # Create a mock implementation
    mock_entity = UserEntity()
    mock_entity.id = user_id
    mock_entity.email = "test@example.com"
    mock_entity.youtube_user_id = "yt123"
    mock_entity.display_name = "Test User"
    mock_entity.preferences_json = {"summary_length": "Standard"}
    mock_entity.to_domain = MagicMock(return_value=User(
        id=user_id,
        email="test@example.com",
        youtube_user_id="yt123",
        display_name="Test User",
        preference_settings=UserPreferences(summary_length="Standard")
    ))
    filter_mock.first.return_value = mock_entity
    
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
    
    # Create mock to handle entity creation
    mock_entity = UserEntity()
    mock_entity.id = user_id
    mock_entity.email = "test@example.com"
    mock_entity.youtube_user_id = "yt123"
    mock_entity.display_name = "Test User"
    mock_entity.to_domain = MagicMock(return_value=User(
        id=user_id,
        email="test@example.com",
        youtube_user_id="yt123",
        display_name="Test User",
        preference_settings=UserPreferences(summary_length="Brief")
    ))
    
    # Setup mocks
    session_mock.add = MagicMock()
    session_mock.commit = MagicMock()
    session_mock.refresh = MagicMock()
    
    # Setup repository
    repo = PostgresUserRepository(session_mock)
    
    # Mock the from_domain static method
    with patch.object(UserEntity, 'from_domain', return_value=mock_entity):
        # Act
        result = repo.create(user)
        
        # Assert
        assert result.id == user_id
        assert result.email == "test@example.com"
        
        session_mock.add.assert_called_once_with(mock_entity)
        session_mock.commit.assert_called_once()
        session_mock.refresh.assert_called_once_with(mock_entity)


def test_update_user():
    # Arrange
    session_mock = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    user_id = uuid.uuid4()
    
    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    
    # Create existing entity
    existing_user_entity = UserEntity()
    existing_user_entity.id = user_id
    existing_user_entity.email = "old@example.com"
    existing_user_entity.youtube_user_id = "yt123"
    existing_user_entity.display_name = "Old Name"
    existing_user_entity.preferences_json = {"summary_length": "Standard"}
    
    # Create updated entity for return value
    updated_entity = UserEntity()
    updated_entity.id = user_id
    updated_entity.email = "new@example.com"
    updated_entity.youtube_user_id = "yt123"
    updated_entity.display_name = "New Name"
    updated_entity.preferences_json = {"summary_length": "Detailed"}
    updated_entity.to_domain = MagicMock(return_value=User(
        id=user_id,
        email="new@example.com",
        youtube_user_id="yt123",
        display_name="New Name",
        preference_settings=UserPreferences(summary_length="Detailed")
    ))
    
    # Setup the first call to return existing entity
    filter_mock.first.return_value = existing_user_entity
    
    # Create domain entity for update
    updated_user = User(
        id=user_id,
        email="new@example.com",
        youtube_user_id="yt123",
        display_name="New Name",
        preference_settings=UserPreferences(summary_length="Detailed")
    )
    
    # Setup repository
    repo = PostgresUserRepository(session_mock)
    
    # Mock refresh to update our entity reference
    def mock_refresh(entity):
        # Mock the refresh by returning the updated entity attributes
        for key, value in updated_entity.__dict__.items():
            if not key.startswith('_') and key != 'to_domain':
                setattr(entity, key, value)
    
    session_mock.refresh.side_effect = mock_refresh
    
    # Act
    result = repo.update(updated_user)
    
    # Assert
    assert result.id == user_id
    assert result.email == "new@example.com"
    assert result.display_name == "New Name"
    
    session_mock.query.assert_called_once_with(UserEntity)
    query_mock.filter.assert_called_once()
    session_mock.commit.assert_called_once()
    session_mock.refresh.assert_called_once_with(existing_user_entity)


def test_delete_user():
    # Arrange
    session_mock = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    user_id = uuid.uuid4()
    
    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    
    # Create mock entity to be deleted
    user_entity = UserEntity()
    user_entity.id = user_id
    user_entity.email = "test@example.com"
    user_entity.youtube_user_id = "yt123"
    user_entity.display_name = "Test User"
    
    # Setup filter mock to return our entity
    filter_mock.first.return_value = user_entity
    
    # Setup repository
    repo = PostgresUserRepository(session_mock)
    
    # Act
    result = repo.delete(user_id)
    
    # Assert
    assert result is True
    
    session_mock.query.assert_called_once_with(UserEntity)
    query_mock.filter.assert_called_once()
    session_mock.delete.assert_called_once_with(user_entity)
    session_mock.commit.assert_called_once()