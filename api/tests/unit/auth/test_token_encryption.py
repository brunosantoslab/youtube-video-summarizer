# api/tests/unit/auth/test_token_encryption.py
import pytest
from infrastructure.auth.token_encryption import TokenEncryption


class TestTokenEncryption:
    """Test token encryption service"""
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        # Setup
        encryption = TokenEncryption(secret_key="test_secret_key_for_encryption_testing")
        
        # Test data
        token_data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "access_token": "ya29.a0AWY7CkmD0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0",
            "refresh_token": "1//0eD0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0D0",
            "expiry": "2023-05-01T10:30:00Z"
        }
        
        # Encrypt
        encrypted = encryption.encrypt_token(token_data)
        
        # Assert encryption produces a string
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
        
        # Decrypt
        decrypted = encryption.decrypt_token(encrypted)
        
        # Assert decryption returns the original data
        assert decrypted == token_data
        assert decrypted["user_id"] == token_data["user_id"]
        assert decrypted["access_token"] == token_data["access_token"]
        assert decrypted["refresh_token"] == token_data["refresh_token"]
        assert decrypted["expiry"] == token_data["expiry"]
    
    def test_decrypt_invalid_token(self):
        """Test decryption of invalid token"""
        # Setup
        encryption = TokenEncryption(secret_key="test_secret_key_for_encryption_testing")
        
        # Try to decrypt invalid token
        with pytest.raises(ValueError):
            encryption.decrypt_token("invalid_token_data")