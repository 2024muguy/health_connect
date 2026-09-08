"""
HealthConnect AI - Core Package
=================================
Core functionality for the application.

This package provides:
- Custom exceptions
- Security utilities
- Event handlers
- Celery configuration
"""

from app.core.exceptions import (
    HealthConnectException,
    DatabaseError,
    LLMProviderError,
    VectorDBError,
    SafetyViolationError,
    RateLimitExceededError,
    ResourceNotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
)

__all__ = [
    "HealthConnectException",
    "DatabaseError",
    "LLMProviderError",
    "VectorDBError",
    "SafetyViolationError",
    "RateLimitExceededError",
    "ResourceNotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
]