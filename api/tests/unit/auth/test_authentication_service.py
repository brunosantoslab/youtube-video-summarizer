"""
Unit tests for authentication service
Author: Bruno Santos
"""
import uuid
from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from application.services.auth.authentication_service import AuthenticationService
from domain.models.auth import OAuthToken, OAuthTokenType


class TestAuthenticationService:
    """Test authentication service"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.oauth_token_repository = MagicMock()
        self.youtube_oauth_service = MagicMock()
        self.auth_service = AuthenticationService(
            youtube_oauth_service=self.youtube_oauth_service,
            oauth_token_repository=self.oauth_token_repository
        )
        
        # Setup common test data
        self.user_id = uuid.uuid4()
        self.token = OAuthToken(
            id=uuid.uuid4(),
            user_id=self.user_id,
            provider=OAuthTokenType.YOUTUBE,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=datetime.now() + timedelta(hours=1)
        )
    
    def test_get_youtube_auth_url(self):
        """Test getting YouTube auth URL"""
        # Setup
        redirect_path = "/dashboard"
        mock_state = "encrypted_state_data"
        mock_auth_url = "https://accounts.google.com/o/oauth2/auth?client_id=123&redirect_uri=..."
        
        self.youtube_oauth_service.create_encrypted_state.return_value = mock_state
        self.youtube_oauth_service.get_authorization_url.return_value = mock_auth_url
        
        # Execute
        result = self.auth_service.get_youtube_auth_url(self.user_id, redirect_path)
        
        # Assert
        assert result == mock_auth_url
        self.youtube_oauth_service.create_encrypted_state.assert_called_once_with(self.user_id, redirect_path)
        self.youtube_oauth_service.get_authorization_url.assert_called_once_with(mock_state)
    
    @pytest.mark.asyncio
    async def test_handle_youtube_callback_success(self):
        """Test handling successful YouTube callback"""
        # Setup
        code = "auth_code"
        state = "encrypted_state"
        user_id = uuid.uuid4()
        redirect_path = "/dashboard"
        
        self.youtube_oauth_service.parse_state.return_value = (user_id, redirect_path)
        self.youtube_oauth_service.exchange_code_for_token = AsyncMock()
        
        # Execute
        success, path = await self.auth_service.handle_youtube_callback(code, state)
        
        # Assert
        assert success is True
        assert path == redirect_path
        self.youtube_oauth_service.parse_state.assert_called_once_with(state)
        self.youtube_oauth_service.exchange_code_for_token.assert_called_once_with(code, user_id)
    
    @pytest.mark.asyncio
    async def test_handle_youtube_callback_failure(self):
        """Test handling failed YouTube callback"""
        # Setup
        code = "auth_code"
        state = "encrypted_state"
        
        self.youtube_oauth_service.parse_state.side_effect = ValueError("Invalid state")
        
        # Execute
        success, path = await self.auth_service.handle_youtube_callback(code, state)
        
        # Assert
        assert success is False
        assert path == "/"
        self.youtube_oauth_service.parse_state.assert_called_once_with(state)
        self.youtube_oauth_service.exchange_code_for_token.assert_not_called()
    
    def test_is_youtube_authenticated_valid(self):
        """Test checking if user is authenticated with valid token"""
        # Setup
        self.oauth_token_repository.get_by_user_id.return_value = self.token
        
        # Execute
        result = self.auth_service.is_youtube_authenticated(self.user_id)
        
        # Assert
        assert result is True
        self.oauth_token_repository.get_by_user_id.assert_called_once_with(self.user_id, "youtube")
    
    def test_is_youtube_authenticated_expired(self):
        """Test checking if user is authenticated with expired token"""
        # Setup
        expired_token = OAuthToken(
            id=uuid.uuid4(),
            user_id=self.user_id,
            provider=OAuthTokenType.YOUTUBE,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=datetime.now() - timedelta(hours=1)
        )
        self.oauth_token_repository.get_by_user_id.return_value = expired_token
        
        # Execute
        result = self.auth_service.is_youtube_authenticated(self.user_id)
        
        # Assert
        assert result is False
        self.oauth_token_repository.get_by_user_id.assert_called_once_with(self.user_id, "youtube")
    
    def test_is_youtube_authenticated_no_token(self):
        """Test checking if user is authenticated with no token"""
        # Setup
        self.oauth_token_repository.get_by_user_id.return_value = None
        
        # Execute
        result = self.auth_service.is_youtube_authenticated(self.user_id)
        
        # Assert
        assert result is False
        self.oauth_token_repository.get_by_user_id.assert_called_once_with(self.user_id, "youtube")
    
    @pytest.mark.asyncio
    async def test_get_youtube_token_valid(self):
        """Test getting a valid YouTube token"""
        # Setup
        self.youtube_oauth_service.get_user_token = AsyncMock(return_value=self.token)
        
        # Execute
        result = await self.auth_service.get_youtube_token(self.user_id)
        
        # Assert
        assert result == self.token
        self.youtube_oauth_service.get_user_token.assert_called_once_with(self.user_id)
    
    @pytest.mark.asyncio
    async def test_get_youtube_token_none(self):
        """Test getting a non-existent YouTube token"""
        # Setup
        self.youtube_oauth_service.get_user_token = AsyncMock(return_value=None)
        
        # Execute
        result = await self.auth_service.get_youtube_token(self.user_id)
        
        # Assert
        assert result is None
        self.youtube_oauth_service.get_user_token.assert_called_once_with(self.user_id)
    
    @pytest.mark.asyncio
    async def test_revoke_youtube_access_success(self):
        """Test revoking YouTube access successfully"""
        # Setup
        self.oauth_token_repository.get_by_user_id.return_value = self.token
        self.youtube_oauth_service.revoke_token = AsyncMock(return_value=True)
        
        # Execute
        result = await self.auth_service.revoke_youtube_access(self.user_id)
        
        # Assert
        assert result is True
        self.oauth_token_repository.get_by_user_id.assert_called_once_with(self.user_id, "youtube")
        self.youtube_oauth_service.revoke_token.assert_called_once_with(self.token)
    
    @pytest.mark.asyncio
    async def test_revoke_youtube_access_no_token(self):
        """Test revoking YouTube access with no token"""
        # Setup
        self.oauth_token_repository.get_by_user_id.return_value = None
        
        # Execute
        result = await self.auth_service.revoke_youtube_access(self.user_id)
        
        # Assert
        assert result is False
        self.oauth_token_repository.get_by_user_id.assert_called_once_with(self.user_id, "youtube")
        self.youtube_oauth_service.revoke_token.assert_not_called()
