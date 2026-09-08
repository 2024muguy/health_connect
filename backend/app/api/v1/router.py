"""
HealthConnect AI - Main API Router
===================================
Aggregates all API v1 endpoint routers.

Endpoints:
- /auth: Authentication
- /chat: Chat/Conversation
- /appointments: Appointment management
- /clinic: Clinic information
- /escalations: Escalation management
- /admin: Admin operations
- /analytics: Analytics
- /webhooks: External webhooks
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    chat,
    appointment,
    clinic,
    escalation,
    admin,
    analytics,
    webhooks,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(appointment.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(clinic.router, prefix="/clinic", tags=["Clinic"])
api_router.include_router(escalation.router, prefix="/escalations", tags=["Escalations"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])