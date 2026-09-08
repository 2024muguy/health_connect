"""
HealthConnect AI - API Endpoints Package
=========================================
Individual endpoint modules for API v1.
"""

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

__all__ = [
    "auth",
    "chat",
    "appointment",
    "clinic",
    "escalation",
    "admin",
    "analytics",
    "webhooks",
]