"""
HealthConnect AI - API Dependencies
====================================
FastAPI dependencies for authentication, database, and services.

Features:
- User authentication dependency
- Database session dependency
- Service instances
- Rate limiting
"""

from typing import Optional, Generator, AsyncGenerator

from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_session, get_async_session
from app.core.security import security_manager
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    TokenExpiredError,
    TokenInvalidError,
)

from config.logging_config import get_logger

logger = get_logger(__name__)

# Security scheme
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        dict: User payload from token
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = security_manager.verify_token(token, expected_type="access")
        return payload
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get current admin user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        dict: Admin user payload
        
    Raises:
        HTTPException: If user is not admin
    """
    roles = current_user.get("roles", [])
    
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[dict]:
    """
    Get optional user (returns None if not authenticated).
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Optional[dict]: User payload or None
    """
    if not credentials:
        return None
    
    try:
        return security_manager.verify_token(credentials.credentials, expected_type="access")
    except Exception:
        return None


def get_chat_service():
    """Get chat service instance"""
    from app.services.chat_service import ChatService
    return ChatService()


def get_appointment_service(db: Session = Depends(get_session)):
    """Get appointment service instance with a DB session."""
    from app.services.appointment_service import AppointmentService
    return AppointmentService(db=db)


def get_escalation_service():
    """Get escalation service instance"""
    from app.services.escalation_service import EscalationService
    return EscalationService()


def get_notification_service():
    """Get notification service instance"""
    from app.services.notification_service import NotificationService
    return NotificationService()


def get_analytics_service():
    """Get analytics service instance"""
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService()


def get_audit_service():
    """Get audit service instance"""
    from app.services.audit_service import AuditService
    return AuditService()