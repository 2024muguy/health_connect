"""
HealthConnect AI - Custom Exceptions
=====================================
Custom exception hierarchy for the application.

Exception categories:
- Base: HealthConnectException
- Database: DatabaseError
- LLM: LLMProviderError
- Vector DB: VectorDBError
- Safety: SafetyViolationError
- Rate Limiting: RateLimitExceededError
- Resources: ResourceNotFoundError
- Validation: ValidationError
- Authentication: AuthenticationError, AuthorizationError
"""

from typing import Optional, Dict, Any


class HealthConnectException(Exception):
    """
    Base exception for all HealthConnect AI errors.
    
    Attributes:
        message: Error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error details
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "internal_error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class DatabaseError(HealthConnectException):
    """Database operation error"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="database_error",
            status_code=500,
            details=details,
        )


class DatabaseConnectionError(DatabaseError):
    """Database connection error"""
    
    def __init__(self, message: str = "Database connection failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="database_connection_error",
            status_code=503,
            details=details,
        )


class LLMProviderError(HealthConnectException):
    """LLM provider error"""
    
    def __init__(self, message: str = "LLM provider error", provider: str = "unknown", details: Optional[Dict] = None):
        error_details = details or {}
        error_details["provider"] = provider
        super().__init__(
            message=message,
            error_code="llm_provider_error",
            status_code=502,
            details=error_details,
        )


class LLMRateLimitError(LLMProviderError):
    """LLM provider rate limit error"""
    
    def __init__(self, provider: str = "unknown", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=f"Rate limit exceeded for {provider}",
            provider=provider,
            details=details,
        )


class LLMTokenLimitError(LLMProviderError):
    """LLM token limit error"""
    
    def __init__(self, provider: str = "unknown", max_tokens: Optional[int] = None):
        details = {"max_tokens": max_tokens} if max_tokens else {}
        super().__init__(
            message=f"Token limit exceeded for {provider}",
            provider=provider,
            details=details,
        )


class VectorDBError(HealthConnectException):
    """Vector database error"""
    
    def __init__(self, message: str = "Vector database operation failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="vector_db_error",
            status_code=500,
            details=details,
        )


class VectorIndexNotFoundError(VectorDBError):
    """Vector index not found error"""
    
    def __init__(self, index_name: str = ""):
        super().__init__(
            message=f"Vector index not found: {index_name}",
            error_code="vector_index_not_found",
            status_code=404,
        )


class SafetyViolationError(HealthConnectException):
    """Safety violation error"""
    
    def __init__(
        self,
        message: str = "Safety violation detected",
        safety_category: str = "unknown",
        action: str = "block",
        risk_score: int = 100,
        details: Optional[Dict] = None,
    ):
        error_details = details or {}
        error_details.update({
            "safety_category": safety_category,
            "action": action,
            "risk_score": risk_score,
        })
        super().__init__(
            message=message,
            error_code="safety_violation",
            status_code=403,
            details=error_details,
        )


class EmergencyDetectedError(SafetyViolationError):
    """Emergency situation detected"""
    
    def __init__(self):
        super().__init__(
            message="Medical emergency detected",
            safety_category="emergency",
            action="emergency_protocol",
            risk_score=100,
        )


class MedicalAdviceRequestError(SafetyViolationError):
    """Medical advice request detected"""
    
    def __init__(self):
        super().__init__(
            message="Medical advice request detected",
            safety_category="medical_advice_request",
            action="block",
            risk_score=80,
        )


class RateLimitExceededError(HealthConnectException):
    """Rate limit exceeded error"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict] = None,
    ):
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after
        super().__init__(
            message=message,
            error_code="rate_limit_exceeded",
            status_code=429,
            details=error_details,
        )


class ResourceNotFoundError(HealthConnectException):
    """Resource not found error"""
    
    def __init__(
        self,
        resource_type: str = "Resource",
        resource_id: str = "",
        details: Optional[Dict] = None,
    ):
        error_details = details or {}
        error_details.update({
            "resource_type": resource_type,
            "resource_id": resource_id,
        })
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code="resource_not_found",
            status_code=404,
            details=error_details,
        )


class ValidationError(HealthConnectException):
    """Validation error"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="validation_error",
            status_code=422,
            details=details,
        )


class AuthenticationError(HealthConnectException):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="authentication_error",
            status_code=401,
            details=details,
        )


class AuthorizationError(HealthConnectException):
    """Authorization error"""
    
    def __init__(self, message: str = "Authorization failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="authorization_error",
            status_code=403,
            details=details,
        )


class TokenExpiredError(AuthenticationError):
    """Token expired error"""
    
    def __init__(self):
        super().__init__(
            message="Authentication token has expired",
            details={"token_expired": True},
        )


class TokenInvalidError(AuthenticationError):
    """Token invalid error"""
    
    def __init__(self):
        super().__init__(
            message="Invalid authentication token",
            details={"token_invalid": True},
        )