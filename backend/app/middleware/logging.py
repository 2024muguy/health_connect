"""
HealthConnect AI - Logging Middleware
======================================
Request/response logging middleware.

Features:
- Request logging with correlation ID
- Response logging
- Performance metrics
- Error logging
"""

import time
import uuid
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.logging_config import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logging middleware for request/response tracking.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request with logging"""
        
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("User-Agent", ""),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} - {str(e)}",
                exc_info=True,
                extra={
                    "correlation_id": correlation_id,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                }
            )
            raise
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response