"""
HealthConnect AI - Schemas Package
===================================
Pydantic schemas for request/response validation.

Schemas:
- Chat schemas
- Appointment schemas
- Escalation schemas
- Admin schemas
- Analytics schemas
"""

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MessageSchema,
    ConversationSchema,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentCancelRequest,
    AppointmentRescheduleRequest,
)
from app.schemas.escalation import (
    EscalationCreate,
    EscalationResponse,
    EscalationUpdate,
)
from app.schemas.admin import (
    AdminStats,
    AdminUserCreate,
    AdminUserResponse,
)
from app.schemas.analytics import (
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    AnalyticsReport,
)

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "MessageSchema",
    "ConversationSchema",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "AppointmentCancelRequest",
    "AppointmentRescheduleRequest",
    "EscalationCreate",
    "EscalationResponse",
    "EscalationUpdate",
    "AdminStats",
    "AdminUserCreate",
    "AdminUserResponse",
    "AnalyticsEventCreate",
    "AnalyticsEventResponse",
    "AnalyticsReport",
]