"""
HealthConnect AI - Doctor Model
================================
Minimal doctor record to satisfy appointments.doctor_id FK.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Boolean

from app.models.base import BaseModel


class Doctor(BaseModel):
    """Doctor record."""

    __tablename__ = "doctors"
    __table_args__ = {"extend_existing": True}

    id = Column(
        String(64),
        primary_key=True,
        default=lambda: f"DOC-{uuid.uuid4().hex[:8].upper()}",
    )
    full_name = Column(String(200), nullable=False)
    specialty = Column(String(100), nullable=True)
    email = Column(String(320), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# NOTE: Do NOT import Appointment at the bottom — causes circular import.
# The FK is resolved automatically as long as Appointment is imported
# somewhere in the app before create_all() runs.
