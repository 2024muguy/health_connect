"""
HealthConnect AI - Error Handler Middleware
============================================
Global error handling middleware.

Features:
- Catch all exceptions
- Structured error responses
- Error logging
- Graceful degradation
"""

from typing import Optional, Dict, Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.logging_config import get_logger
from app.core.exceptions import HealthConnectException

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware.
    Catches all exceptions and returns structured responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request with error handling"""
        try:
            response = await call_next(request)
            return response
        
        except HealthConnectException as e:
            # Handle known exceptions
            logger.error(f"HealthConnectException: {e.message}", extra={
                "error_code": e.error_code,
                "path": request.url.path,
            })
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": e.error_code,
                        "message": e.message,
                        "details": e.details,
                    },
                },
            )
        
        except Exception as e:
            # Handle unknown exceptions
            logger.critical(f"Unhandled exception: {str(e)}", exc_info=True, extra={
                "path": request.url.path,
            })
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "internal_error",
                        "message": "An internal server error occurred",
                        "details": None,
                    },
                },
            )