# api/infrastructure/auth/token_encryption.py
import base64
from typing import Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json

from config import get_settings


class TokenEncryption:
    """Service for encrypting and decrypting OAuth tokens"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or get_settings().secret_key
        self.fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """Create a Fernet cipher using the application secret key"""
        # Derive a key from the secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'youtube_video_summarizer',
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return Fernet(key)
    
    def encrypt_token(self, token_data: Dict[str, Any]) -> str:
        """
        Encrypt an OAuth token
        
        Args:
            token_data: Token data to encrypt
            
        Returns:
            Encrypted token string
        """
        token_json = json.dumps(token_data)
        encrypted_token = self.fernet.encrypt(token_json.encode())
        return base64.urlsafe_b64encode(encrypted_token).decode()
    
    def decrypt_token(self, encrypted_token: str) -> Dict[str, Any]:
        """
        Decrypt an OAuth token
        
        Args:
            encrypted_token: Encrypted token string
            
        Returns:
            Decrypted token data
        """
        try:
            decoded = base64.urlsafe_b64decode(encrypted_token)
            decrypted_token = self.fernet.decrypt(decoded)
            return json.loads(decrypted_token.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt token: {str(e)}")
