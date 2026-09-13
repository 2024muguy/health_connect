"""
HealthConnect AI - FastAPI Application Entry Point
===================================================
Main application factory with comprehensive middleware setup.

Features:
- Application factory pattern
- CORS configuration
- Rate limiting
- Prometheus monitoring
- Structured logging
- Exception handlers
- Health check endpoints
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from prometheus_fastapi_instrumentator import Instrumentator

from config.settings import get_settings
from config.logging_config import setup_logging, get_logger
from config.constants import APP_NAME, APP_VERSION, APP_DESCRIPTION

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
from app.core.events import (
    on_startup,
    on_shutdown,
)
from app.api.v1.router import api_router
from app.database.session import engine
from app.models.base import Base
from app.models.user import User  # noqa: F401 — registers table
from app.models.doctor import Doctor  # noqa: F401 — registers FK target

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    environment=settings.ENVIRONMENT,
    log_file=f"logs/{settings.ENVIRONMENT}.log",
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Startup
    await on_startup(app)
    
    yield
    
    # Shutdown
    await on_shutdown(app)
    logger.info(f"{APP_NAME} shutdown complete")


def _init_db() -> None:
    """Create all database tables in the configured DB (SQLite or Neon)."""
    import traceback
    try:
        from app.database.session import engine
        from app.models.base import Base

        # Import order matters — FK targets must come first
        from app.models.user import User                            # noqa: F401
        from app.models.doctor import Doctor                        # noqa: F401
        from app.models.patient import Patient                      # noqa: F401
        from app.models.appointment import Appointment              # noqa: F401
        try:
            from app.models.conversation import Conversation        # noqa: F401
        except Exception as e:
            print(f"  ⚠️ Conversation: {e}")
        try:
            from app.models.message import Message                  # noqa: F401
        except Exception as e:
            print(f"  ⚠️ Message: {e}")
        try:
            from app.models.escalation import Escalation            # noqa: F401
        except Exception as e:
            print(f"  ⚠️ Escalation: {e}")
        try:
            from app.models.knowledge_chunk import KnowledgeChunk   # noqa: F401
        except Exception as e:
            print(f"  ⚠️ KnowledgeChunk: {e}")

        print(f"📦 Engine: {engine.url}")
        print(f"📦 Tables registered: {sorted(Base.metadata.tables.keys())}")

        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ensured")
    except Exception as e:
        print(f"❌ DB init failed: {e}")
        traceback.print_exc()




def create_app() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    _init_db()

    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json",
    )

    # ============================================
    # CORS Middleware
    # ============================================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=settings.cors_methods_list,
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )

    # ============================================
    # Trusted Host Middleware
    # ============================================
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["healthconnect.ai", "*.healthconnect.ai", "localhost"],
        )

    # ============================================
    # GZip Compression
    # ============================================
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ============================================
    # Prometheus Monitoring
    # ============================================
    if settings.monitoring.ENABLED:
        instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=[".*admin.*", "/metrics"],
            inprogress_name="http_requests_inprogress",
            inprogress_labels=True,
        )
        instrumentator.instrument(app).expose(app, endpoint="/metrics")

    # ============================================
    # Exception Handlers
    # ============================================
    @app.exception_handler(HealthConnectException)
    async def healthconnect_exception_handler(request: Request, exc: HealthConnectException):
        """Handle custom HealthConnect exceptions"""
        logger.error(f"HealthConnectException: {exc.message}", extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTPException: {exc.detail}", extra={
            "status_code": exc.status_code,
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "http_error",
                    "message": str(exc.detail),
                    "details": None,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        logger.warning(f"ValidationError: {exc.errors()}", extra={
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions"""
        logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True, extra={
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "internal_error",
                    "message": "An internal server error occurred",
                    "details": None,
                },
            },
        )

    # ============================================
    # Middleware for Request ID
    # ============================================
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add request ID to all responses"""
        import uuid
        
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

    # ============================================
    # Middleware for Logging
    # ============================================
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests"""
        import time
        
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "request_id": getattr(request.state, "request_id", None),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return response

    # ============================================
    # Health Check Endpoint
    # ============================================
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "app": APP_NAME,
            "version": APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }

    @app.get("/ready", tags=["Health"])
    async def readiness_check():
        """Readiness check endpoint"""
        # Check database connection
        from app.database.connection import check_database_connection
        db_ready = await check_database_connection()
        
        # Check Redis connection
        from app.utils.cache import check_redis_connection
        redis_ready = await check_redis_connection()
        
        # Check LLM providers
        from app.llm.provider_factory import check_llm_providers
        llm_ready = await check_llm_providers()
        
        return {
            "status": "ready" if all([db_ready, redis_ready, llm_ready]) else "not_ready",
            "checks": {
                "database": "up" if db_ready else "down",
                "redis": "up" if redis_ready else "down",
                "llm": "up" if llm_ready else "down",
            },
        }

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "app": APP_NAME,
            "version": APP_VERSION,
            "docs": "/docs",
            "health": "/health",
            "api": settings.API_PREFIX,
        }

    # ============================================
    # Include API Router
    # ============================================
    app.include_router(api_router, prefix=settings.API_PREFIX)

    logger.info(f"{APP_NAME} application created successfully")
    
    return app


# Create application instance
app = create_app()