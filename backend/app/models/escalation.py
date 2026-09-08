"""
HealthConnect AI - Escalation Model
====================================
Escalation database model for tracking human escalations.

Fields:
- Escalation type and tier
- Department routing
- Status tracking
- Resolution information
"""

import uuid
from datetime import datetime, timezone
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
    Text,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class EscalationStatus(enum.Enum):
    """Escalation status enumeration"""
    
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class EscalationTier(enum.Enum):
    """Escalation tier enumeration"""
    
    TIER_0 = 0  # AI Resolution
    TIER_1 = 1  # Guided Self-Service
    TIER_2 = 2  # Action Escalation
    TIER_3 = 3  # Knowledge Escalation
    TIER_4 = 4  # Safety Escalation
    TIER_5 = 5  # Emergency Protocol


class EscalationType(enum.Enum):
    """Escalation type enumeration"""
    
    APPOINTMENT = "appointment"
    BILLING = "billing"
    INSURANCE = "insurance"
    CLINICAL = "clinical"
    SAFETY = "safety"
    EMERGENCY = "emergency"
    TECHNICAL = "technical"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    OTHER = "other"


class Escalation(BaseModel):
    """
    Escalation model for tracking human escalations.
    """
    
    __tablename__ = "escalations"
    
    # ============================================
    # Escalation Identification
    # ============================================
    escalation_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique escalation code (ESC-XXXXXXXX)",
    )
    
    # ============================================
    # Foreign Keys
    # ============================================
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to conversation",
    )
    
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to patient",
    )
    
    # ============================================
    # Escalation Details
    # ============================================
    escalation_type = Column(
        Enum(EscalationType, name="escalation_type_enum"),
        nullable=False,
        comment="Type of escalation",
    )
    
    tier = Column(
        Enum(EscalationTier, name="escalation_tier_enum"),
        nullable=False,
        comment="Escalation tier",
    )
    
    status = Column(
        Enum(EscalationStatus, name="escalation_status_enum"),
        default=EscalationStatus.PENDING,
        nullable=False,
        index=True,
        comment="Escalation status",
    )
    
    priority = Column(
        String(20),
        default="normal",
        nullable=False,
        comment="Priority (low, normal, high, critical)",
    )
    
    department = Column(
        String(100),
        nullable=True,
        comment="Department to route to",
    )
    
    # ============================================
    # Escalation Content
    # ============================================
    reason = Column(
        Text,
        nullable=False,
        comment="Reason for escalation",
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description",
    )
    
    context = Column(
        JSON,
        nullable=True,
        comment="Conversation context at time of escalation",
    )
    
    # ============================================
    # Assignment
    # ============================================
    assigned_to = Column(
        String(100),
        nullable=True,
        comment="Staff member assigned",
    )
    
    assigned_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Assignment timestamp",
    )
    
    # ============================================
    # Resolution
    # ============================================
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Resolution timestamp",
    )
    
    resolution = Column(
        Text,
        nullable=True,
        comment="Resolution details",
    )
    
    resolved_by = Column(
        String(100),
        nullable=True,
        comment="Staff member who resolved",
    )
    
    # ============================================
    # Relationships
    # ============================================
    conversation = relationship(
        "Conversation",
        back_populates="escalations",
        lazy="joined",
    )
    
    # ============================================
    # Indexes
    # ============================================
    __table_args__ = (
        Index("idx_escalation_conversation", "conversation_id"),
        Index("idx_escalation_patient", "patient_id"),
        Index("idx_escalation_status", "status"),
        Index("idx_escalation_type", "escalation_type"),
        Index("idx_escalation_priority", "priority"),
    )
    
    @property
    def is_pending(self) -> bool:
        """Check if escalation is pending"""
        return self.status == EscalationStatus.PENDING
    
    @property
    def is_resolved(self) -> bool:
        """Check if escalation is resolved"""
        return self.status in [EscalationStatus.RESOLVED, EscalationStatus.CLOSED]
    
    @property
    def is_critical(self) -> bool:
        """Check if escalation is critical"""
        return self.priority == "critical" or self.tier in [EscalationTier.TIER_4, EscalationTier.TIER_5]
    
    def assign(self, staff_member: str) -> None:
        """Assign escalation to staff member"""
        self.assigned_to = staff_member
        self.assigned_at = datetime.now(timezone.utc)
        self.status = EscalationStatus.ASSIGNED
    
    def resolve(self, resolution: str, resolved_by: str) -> None:
        """Mark escalation as resolved"""
        self.resolution = resolution
        self.resolved_by = resolved_by
        self.resolved_at = datetime.now(timezone.utc)
        self.status = EscalationStatus.RESOLVED