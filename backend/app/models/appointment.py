"""
HealthConnect AI - Appointment Model
=====================================
Appointment database model.

Fields:
- Appointment details (type, date, time)
- Status tracking
- Reminder information
- No-show tracking
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    Float,
    Text,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, SoftDeleteMixin


class AppointmentStatus(enum.Enum):
    """Appointment status enumeration"""
    
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"
    PENDING = "pending"


class AppointmentType(enum.Enum):
    """Appointment type enumeration"""
    
    GENERAL = "general"
    FOLLOW_UP = "follow_up"
    SPECIALIST = "specialist"
    LAB = "lab"
    IMAGING = "imaging"
    VACCINATION = "vaccination"
    PHYSICAL = "physical"
    CONSULTATION = "consultation"
    URGENT_CARE = "urgent_care"
    TELEHEALTH = "telehealth"


class Appointment(BaseModel, SoftDeleteMixin):
    """
    Appointment model for tracking patient appointments.
    """
    
    __tablename__ = "appointments"
    
    # ============================================
    # Appointment Identification
    # ============================================
    appointment_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique appointment code (APT-XXXXXXXX)",
    )
    
    # ============================================
    # Foreign Keys
    # ============================================
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to patient",
    )
    
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to doctor",
    )
    
    # ============================================
    # Appointment Details
    # ============================================
    appointment_type = Column(
        Enum(AppointmentType, name="appointment_type_enum"),
        nullable=False,
        default=AppointmentType.GENERAL,
        comment="Type of appointment",
    )
    
    status = Column(
        Enum(AppointmentStatus, name="appointment_status_enum"),
        nullable=False,
        default=AppointmentStatus.SCHEDULED,
        index=True,
        comment="Appointment status",
    )
    
    scheduled_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Scheduled appointment datetime",
    )
    
    duration_minutes = Column(
        Integer,
        default=30,
        nullable=False,
        comment="Appointment duration in minutes",
    )
    
    reason = Column(
        Text,
        nullable=True,
        comment="Reason for appointment",
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes",
    )
    
    # ============================================
    # Location Information
    # ============================================
    clinic_location = Column(
        String(255),
        nullable=True,
        comment="Clinic location name",
    )
    
    room_number = Column(
        String(50),
        nullable=True,
        comment="Room number",
    )
    
    # ============================================
    # Reminder Information
    # ============================================
    reminder_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether reminder was sent",
    )
    
    reminder_sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When reminder was sent",
    )
    
    reminder_method = Column(
        String(20),
        nullable=True,
        comment="Reminder method (email, sms, phone)",
    )
    
    # ============================================
    # No-Show Tracking
    # ============================================
    no_show = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether patient was a no-show",
    )
    
    no_show_reason = Column(
        Text,
        nullable=True,
        comment="Reason for no-show (if known)",
    )
    
    # ============================================
    # Timing Information
    # ============================================
    checked_in_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Patient check-in time",
    )
    
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Appointment completion time",
    )
    
    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Cancellation time",
    )
    
    cancelled_reason = Column(
        Text,
        nullable=True,
        comment="Cancellation reason",
    )
    
    # ============================================
    # Distance Information
    # ============================================
    distance_to_clinic = Column(
        Float,
        nullable=True,
        comment="Distance to clinic in miles",
    )
    
    # ============================================
    # Relationships
    # ============================================
    patient = relationship(
        "Patient",
        back_populates="appointments",
        lazy="joined",
    )
    
    # ============================================
    # Indexes and Constraints
    # ============================================
    __table_args__ = (
        Index("idx_appointment_patient", "patient_id"),
        Index("idx_appointment_datetime", "scheduled_datetime"),
        Index("idx_appointment_status", "status"),
        Index("idx_appointment_no_show", "no_show"),
        Index("idx_appointment_patient_datetime", "patient_id", "scheduled_datetime"),
        CheckConstraint(
            "duration_minutes > 0",
            name="ck_appointment_duration_positive",
        ),
    )
    
    @property
    def is_upcoming(self) -> bool:
        """Check if appointment is in the future"""
        return self.scheduled_datetime > datetime.now(timezone.utc)
    
    @property
    def is_past(self) -> bool:
        """Check if appointment is in the past"""
        return self.scheduled_datetime < datetime.now(timezone.utc)
    
    @property
    def can_cancel(self) -> bool:
        """Check if appointment can be cancelled"""
        if self.status != AppointmentStatus.SCHEDULED:
            return False
        
        if not self.is_upcoming:
            return False
        
        # Must be at least 24 hours before appointment
        return self.scheduled_datetime - datetime.now(timezone.utc) > timedelta(hours=24)
    
    @property
    def can_reschedule(self) -> bool:
        """Check if appointment can be rescheduled"""
        return self.can_cancel
    
    @property
    def is_no_show_risk(self) -> bool:
        """Check if appointment is at risk of no-show"""
        # Simple risk factors
        risk_factors = []
        
        if self.distance_to_clinic and self.distance_to_clinic > 10:
            risk_factors.append("far_distance")
        
        if not self.reminder_sent:
            risk_factors.append("no_reminder")
        
        if self.scheduled_datetime.hour < 9 or self.scheduled_datetime.hour >= 17:
            risk_factors.append("off_hours")
        
        return len(risk_factors) >= 2
    
    def mark_confirmed(self) -> None:
        """Mark appointment as confirmed"""
        self.status = AppointmentStatus.CONFIRMED
    
    def mark_checked_in(self) -> None:
        """Mark patient as checked in"""
        self.status = AppointmentStatus.CHECKED_IN
        self.checked_in_at = datetime.now(timezone.utc)
    
    def mark_completed(self) -> None:
        """Mark appointment as completed"""
        self.status = AppointmentStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
    
    def mark_cancelled(self, reason: str = "") -> None:
        """Mark appointment as cancelled"""
        self.status = AppointmentStatus.CANCELLED
        self.cancelled_at = datetime.now(timezone.utc)
        self.cancelled_reason = reason
    
    def mark_no_show(self, reason: str = "") -> None:
        """Mark patient as no-show"""
        self.status = AppointmentStatus.NO_SHOW
        self.no_show = True
        self.no_show_reason = reason