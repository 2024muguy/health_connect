"""
HealthConnect AI - Admin Endpoints
===================================
Admin dashboard and management endpoints.

Endpoints:
- GET /admin/stats: Dashboard statistics
- GET /admin/users: List users
- POST /admin/users: Create user
- GET /admin/system: System information
- POST /admin/maintenance: Toggle maintenance mode
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_current_admin, get_analytics_service, get_audit_service
from app.schemas.admin import AdminStats, AdminUserCreate, AdminUserResponse

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: dict = Depends(get_current_admin),
    analytics_service = Depends(get_analytics_service),
):
    """
    Get admin dashboard statistics (admin only).
    """
    metrics = await analytics_service.get_metrics()
    
    return AdminStats(
        total_patients=0,  # Would query database
        total_appointments=metrics.get("total_appointments", 0),
        total_conversations=metrics.get("total_conversations", 0),
        total_escalations=metrics.get("total_escalations", 0),
        pending_escalations=0,
        critical_escalations=0,
        no_show_rate=metrics.get("no_show_rate", 0.0),
        average_response_time_ms=metrics.get("average_response_time_ms", 0),
        average_satisfaction=0.0,
        active_conversations=0,
        appointments_today=0,
        appointments_this_week=0,
    )


@router.get("/system")
async def get_system_info(
    current_user: dict = Depends(get_current_admin),
):
    """
    Get system information (admin only).
    """
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "api_prefix": settings.API_PREFIX,
    }


@router.get("/users")
async def list_users(
    limit: int = Query(default=50, le=100),
    current_user: dict = Depends(get_current_admin),
):
    """
    List users (admin only).
    """
    # Placeholder
    return {
        "users": [],
        "total": 0,
        "limit": limit,
    }


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: AdminUserCreate,
    current_user: dict = Depends(get_current_admin),
):
    """
    Create a new user (admin only).
    """
    # Placeholder
    return {
        "status": "created",
        "email": request.email,
        "full_name": request.full_name,
        "role": request.role,
    }


@router.get("/audit")
async def get_audit_trail(
    event_type: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=500),
    current_user: dict = Depends(get_current_admin),
    audit_service = Depends(get_audit_service),
):
    """
    Get audit trail (admin only).
    """
    events = await audit_service.get_audit_trail(
        event_type=event_type,
        severity=severity,
        limit=limit,
    )
    
    return {
        "events": events,
        "total": len(events),
    }


@router.get("/audit/security")
async def get_security_events(
    limit: int = Query(default=50, le=200),
    current_user: dict = Depends(get_current_admin),
    audit_service = Depends(get_audit_service),
):
    """
    Get security events (admin only).
    """
    events = await audit_service.get_security_events(limit=limit)
    
    return {
        "security_events": events,
        "total": len(events),
    }