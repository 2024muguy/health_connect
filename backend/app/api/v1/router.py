"""
HealthConnect AI - API v1 Router
=================================
Aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    notifications,
    chat,
    appointment,
    clinic,
    escalation,
    admin,
    analytics,
    webhooks,
)

# WebSocket router — imported separately to avoid circular dependency

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(appointment.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(clinic.router, prefix="/clinic", tags=["Clinic"])
api_router.include_router(escalation.router, prefix="/escalations", tags=["Escalations"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# WebSocket (no prefix — matches /ws/chat/{id})
