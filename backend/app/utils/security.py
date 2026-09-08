"""
HealthConnect AI - Security Utilities
======================================
Security helper functions.

Features:
- Data sanitization
- Input escaping
- PII detection
- Data masking
- Secure token generation
- Rate limiting helpers
"""

import re
import hashlib
import secrets
from typing import Optional, List, Dict, Any
import html

from config.logging_config import get_logger

logger = get_logger(__name__)


class PIIDetector:
    """Detect Personally Identifiable Information (PII)"""
    
    # PII Patterns
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        "date_of_birth": r'\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b',
        "address": r'\b\d+\s+[A-Za-z]+\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)\b',
        "zip_code": r'\b\d{5}(?:-\d{4})?\b',
    }
    
    @classmethod
    def detect(cls, text: str) -> List[Dict[str, str]]:
        """
        Detect PII in text.
        
        Args:
            text: Text to scan
            
        Returns:
            List[Dict]: Detected PII with type and value
        """
        detected = []
        
        for pii_type, pattern in cls.PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                })
        
        return detected
    
    @classmethod
    def has_pii(cls, text: str) -> bool:
        """Check if text contains PII"""
        return len(cls.detect(text)) > 0
    
    @classmethod
    def mask_pii(cls, text: str) -> str:
        """
        Mask PII in text.
        
        Args:
            text: Text to mask
            
        Returns:
            str: Text with PII masked
        """
        for pii_type, pattern in cls.PATTERNS.items():
            text = re.sub(
                pattern,
                lambda m: cls._mask_value(m.group(), pii_type),
                text,
                flags=re.IGNORECASE,
            )
        
        return text
    
    @classmethod
    def _mask_value(cls, value: str, pii_type: str) -> str:
        """Mask a PII value"""
        if pii_type == "email":
            parts = value.split("@")
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                if len(username) > 2:
                    return f"{username[:2]}***@{domain}"
                return f"***@{domain}"
        
        if pii_type == "phone":
            digits = re.sub(r'\D', '', value)
            if len(digits) >= 4:
                return f"***-***-{digits[-4:]}"
        
        if pii_type == "ssn":
            return f"***-**-{value[-4:]}"
        
        if pii_type == "credit_card":
            digits = re.sub(r'\D', '', value)
            if len(digits) >= 4:
                return f"****-****-****-{digits[-4:]}"
        
        # Default: mask all but last 4 chars
        if len(value) > 4:
            return "*" * (len(value) - 4) + value[-4:]
        return "****"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input.
    Removes HTML tags and escapes special characters.
    
    Args:
        text: Input text
        
    Returns:
        str: Sanitized text
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape HTML entities
    text = html.escape(text)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    # Remove path components
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:195] + (f'.{ext}' if ext else '')
    
    return filename


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure token.
    
    Args:
        length: Token length in bytes
        
    Returns:
        str: URL-safe token
    """
    return secrets.token_urlsafe(length)


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of data.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm
        
    Returns:
        str: Hex digest
    """
    if algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data showing only last N characters.
    
    Args:
        data: Data to mask
        visible_chars: Number of visible characters at end
        
    Returns:
        str: Masked data
    """
    if not data:
        return ""
    
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def create_api_signature(payload: Dict[str, Any], secret_key: str) -> str:
    """
    Create HMAC signature for API payload.
    
    Args:
        payload: Request payload
        secret_key: Secret key for signing
        
    Returns:
        str: HMAC signature
    """
    import hmac
    import json
    
    # Sort keys for consistency
    sorted_payload = json.dumps(payload, sort_keys=True)
    
    signature = hmac.new(
        secret_key.encode(),
        sorted_payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    
    return signature


def verify_api_signature(
    payload: Dict[str, Any],
    signature: str,
    secret_key: str,
) -> bool:
    """
    Verify HMAC signature.
    
    Args:
        payload: Request payload
        signature: Expected signature
        secret_key: Secret key
        
    Returns:
        bool: True if signature is valid
    """
    expected = create_api_signature(payload, secret_key)
    return hmac.compare_digest(expected, signature)