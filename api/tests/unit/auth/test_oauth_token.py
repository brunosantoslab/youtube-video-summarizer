# api/tests/unit/auth/test_oauth_token.py
import uuid
from datetime import datetime, timedelta
import pytest

from domain.models.auth import OAuthToken, OAuthTokenType


class TestOAuthToken:
    """Test OAuth token domain entity"""
    
    def test_init(self):
        """Test token initialization"""
        token_id = uuid.uuid4()
        user_id = uuid.uuid4()
        now = datetime.now()
        expires = now + timedelta(hours=1)
        
        token = OAuthToken(
            id=token_id,
            user_id=user_id,
            provider=OAuthTokenType.YOUTUBE,
            access_token="access_token_value",
            refresh_token="refresh_token_value",
            token_type="Bearer",
            scope="scope1 scope2",
            expires_at=expires,
            created_at=now,
            updated_at=now
        )
        
        assert token.id == token_id
        assert token.user_id == user_id
        assert token.provider == OAuthTokenType.YOUTUBE
        assert token.access_token == "access_token_value"
        assert token.refresh_token == "refresh_token_value"
        assert token.token_type == "Bearer"
        assert token.scope == "scope1 scope2"
        assert token.expires_at == expires
        assert token.date_created == now
        assert token.date_modified == now
    
    def test_is_expired(self):
        """Test token expiration checking"""
        # Expired token
        token1 = OAuthToken(
            expires_at=datetime.now() - timedelta(hours=1)
        )
        assert token1.is_expired is True
        
        # Valid token
        token2 = OAuthToken(
            expires_at=datetime.now() + timedelta(hours=1)
        )
        assert token2.is_expired is False
        
        # No expiration (should be treated as expired)
        token3 = OAuthToken(
            expires_at=None
        )
        assert token3.is_expired is True
    
    def test_authorization_header(self):
        """Test authorization header generation"""
        token = OAuthToken(
            access_token="my_access_token",
            token_type="Bearer"
        )
        assert token.authorization_header == "Bearer my_access_token"
        
        # Different token type
        token2 = OAuthToken(
            access_token="my_access_token",
            token_type="MAC"
        )
        assert token2.authorization_header == "MAC my_access_token"