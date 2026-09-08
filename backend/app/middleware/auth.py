"""
HealthConnect AI - Authentication Middleware
=============================================
JWT authentication middleware.

Features:
- JWT token validation
- User context injection
- Role-based access control
- Token refresh handling
"""

from typing import Optional, Dict, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import get_settings
from config.logging_config import get_logger
from app.core.security import security_manager
from app.core.exceptions import AuthenticationError, AuthorizationError, TokenExpiredError

logger = get_logger(__name__)
settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT authentication middleware.
    Validates tokens and injects user context.
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = [
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/public",
    ]
    
    # Admin-only endpoints
    ADMIN_PATHS = [
        "/api/v1/admin",
        "/api/v1/analytics",
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication"""
        
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # Get token from header
        token = self._extract_token(request)
        
        if not token:
            raise AuthenticationError("Authentication required")
        
        # Validate token
        try:
            payload = security_manager.verify_token(token, expected_type="access")
        except TokenExpiredError:
            raise
        except Exception:
            raise AuthenticationError("Invalid authentication token")
        
        # Set user context
        request.state.user_id = payload.get("sub")
        request.state.user_roles = payload.get("roles", [])
        request.state.token_payload = payload
        
        # Check admin access
        if self._is_admin_path(request.url.path):
            if "admin" not in request.state.user_roles:
                raise AuthorizationError("Admin access required")
        
        # Process request
        response = await call_next(request)
        
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public"""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False
    
    def _is_admin_path(self, path: str) -> bool:
        """Check if path requires admin access"""
        for admin_path in self.ADMIN_PATHS:
            if path.startswith(admin_path):
                return True
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request"""
        # Try Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        # Try X-API-Key header
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return api_key
        
        # Try cookie
        token = request.cookies.get("access_token")
        if token:
            return token
        
        return None