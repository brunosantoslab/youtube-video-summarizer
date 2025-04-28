"""
Integration tests for YouTube OAuth flow using TestContainers
Author: Bruno Santos
"""
import pytest
from httpx import AsyncClient
import uuid
from sqlalchemy.orm import Session

from domain.models.user import User
from domain.repositories.user_repository import IUserRepository
from infrastructure.repositories.repository_factory import get_repository_factory


@pytest.mark.integration
class TestYouTubeOAuthFlow:
    """Integration tests for YouTube OAuth flow"""
    
    @pytest.mark.asyncio
    async def test_get_auth_url(self, client, db_session, mock_settings):
        """Test getting auth URL endpoint"""
        # Setup
        repository_factory = get_repository_factory(db_session)
        user_repo = repository_factory.get(IUserRepository)
        
        # Create a test user
        user = User(
            email="test@example.com",
            youtube_user_id="test_youtube_id",
            display_name="Test User"
        )
        user = user_repo.create(user)
        db_session.commit()
        
        # Make request
        response = await client.get(f"/api/auth/youtube/auth-url?user_id={user.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert isinstance(data["auth_url"], str)
        assert "accounts.google.com/o/oauth2/auth" in data["auth_url"]
    
    @pytest.mark.asyncio
    async def test_check_auth_status_unauthenticated(self, client, db_session, mock_settings):
        """Test checking auth status when not authenticated"""
        # Setup
        repository_factory = get_repository_factory(db_session)
        user_repo = repository_factory.get(IUserRepository)
        
        # Create a test user
        user = User(
            email="test2@example.com",
            youtube_user_id="test_youtube_id2",
            display_name="Test User 2"
        )
        user = user_repo.create(user)
        db_session.commit()
        
        # Make request
        response = await client.get(f"/api/auth/youtube/status?user_id={user.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data
        assert data["authenticated"] is False
        assert data["scopes"] is None
