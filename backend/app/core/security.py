"""
HealthConnect AI - Security Core
=================================
Security utilities for authentication, encryption, and data protection.

Features:
- JWT token creation and validation
- Password hashing
- Data encryption
- API key validation
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple

from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from config.settings import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT algorithm
JWT_ALGORITHM = "HS256"


class SecurityManager:
    """
    Security manager for authentication and encryption operations.
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self._fernet_key = self._derive_fernet_key()
        self._fernet = Fernet(self._fernet_key)
    
    def _derive_fernet_key(self) -> bytes:
        """Derive Fernet key from secret key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"healthconnect-salt",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return key
    
    # ============================================
    # Password Hashing
    # ============================================
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    # ============================================
    # JWT Token Management
    # ============================================
    def create_access_token(
        self,
        subject: str,
        extra_claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            subject: Token subject (usually user ID)
            extra_claims: Additional claims to include
            expires_delta: Token expiration time
            
        Returns:
            str: JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        now = datetime.now(timezone.utc)
        expires_at = now + expires_delta
        
        payload = {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
            "type": "access",
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=JWT_ALGORITHM)
    
    def create_refresh_token(
        self,
        subject: str,
        extra_claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            subject: Token subject
            extra_claims: Additional claims
            expires_delta: Token expiration
            
        Returns:
            str: JWT refresh token
        """
        if expires_delta is None:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        now = datetime.now(timezone.utc)
        expires_at = now + expires_delta
        
        payload = {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
            "type": "refresh",
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=JWT_ALGORITHM)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Dict: Token payload
            
        Raises:
            TokenExpiredError: If token has expired
            TokenInvalidError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError:
            raise TokenInvalidError()
    
    def verify_token(self, token: str, expected_type: str = "access") -> Dict[str, Any]:
        """
        Verify token and check type.
        
        Args:
            token: JWT token
            expected_type: Expected token type
            
        Returns:
            Dict: Token payload
        """
        payload = self.decode_token(token)
        
        if payload.get("type") != expected_type:
            raise TokenInvalidError()
        
        return payload
    
    # ============================================
    # Data Encryption
    # ============================================
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data"""
        return self._fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self._fernet.decrypt(encrypted_data.encode()).decode()
    
    # ============================================
    # API Key Management
    # ============================================
    def generate_api_key(self) -> Tuple[str, str]:
        """
        Generate an API key pair.
        
        Returns:
            Tuple[str, str]: (api_key, api_key_hash)
        """
        api_key = secrets.token_urlsafe(32)
        api_key_hash = self.hash_api_key(api_key)
        return api_key, api_key_hash
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key(self, api_key: str, api_key_hash: str) -> bool:
        """Verify API key against hash"""
        return hmac.compare_digest(
            self.hash_api_key(api_key),
            api_key_hash,
        )
    
    # ============================================
    # Token Generation
    # ============================================
    def generate_random_token(self, length: int = 32) -> str:
        """Generate a random token"""
        return secrets.token_urlsafe(length)
    
    def generate_correlation_id(self) -> str:
        """Generate a correlation ID"""
        return secrets.token_hex(16)


# Singleton instance
security_manager = SecurityManager()

# ============================================================
# Password Hashing
# ============================================================
from passlib.context import CryptContext

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _password_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return _password_context.verify(plain, hashed)
    except Exception:
        return False


# ============================================================
# Password Hashing (direct bcrypt — no passlib)
# ============================================================
import bcrypt as _bcrypt


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt directly."""
    if isinstance(plain, str):
        plain = plain.encode("utf-8")
    plain = plain[:72]  # bcrypt 72-byte limit
    return _bcrypt.hashpw(plain, _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        if isinstance(plain, str):
            plain = plain.encode("utf-8")
        if isinstance(hashed, str):
            hashed = hashed.encode("utf-8")
        return _bcrypt.checkpw(plain[:72], hashed)
    except Exception:
        return False
