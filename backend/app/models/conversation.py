"""
HealthConnect AI - Conversation Model
======================================
Conversation database model for chat sessions.

Fields:
- Session information
- Patient reference
- Conversation status
- Summary and metadata
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
import enum

from sqlalchemy import (
    Text,
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

from app.models.base import BaseModel, SoftDeleteMixin


class ConversationStatus(enum.Enum):
    """Conversation status enumeration"""
    
    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"
    ABANDONED = "abandoned"
    BLOCKED = "blocked"


class Conversation(BaseModel):
    """
    Conversation model for tracking chat sessions.
    """
    
    __tablename__ = "conversations"
    
    # ============================================
    # Conversation Identification
    # ============================================
    conversation_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique conversation code (CONV-XXXXXXXX)",
    )
    
    session_token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Session token for this conversation",
    )
    
    # ============================================
    # Foreign Keys
    # ============================================
    patient_id = Column(
        String(64),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to patient (if known)",
    )
    
    # ============================================
    # Conversation Details
    # ============================================
    status = Column(
        Enum(ConversationStatus, name="conversation_status_enum"),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        index=True,
        comment="Conversation status",
    )
    
    channel = Column(
        String(50),
        default="web",
        nullable=False,
        comment="Communication channel (web, mobile, api)",
    )
    
    language = Column(
        String(10),
        default="en",
        nullable=False,
        comment="Conversation language",
    )
    
    # ============================================
    # Timing Information
    # ============================================
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Conversation start time",
    )
    
    ended_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Conversation end time",
    )
    
    last_activity_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Last activity timestamp",
    )
    
    # ============================================
    # Conversation Content
    # ============================================
    summary = Column(
        Text,
        nullable=True,
        comment="Auto-generated conversation summary",
    )

    facts_json = Column(
        Text,
        nullable=True,
        comment="Structured facts extracted from the conversation (JSON)",
    )
    
    conversation_model_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional conversation metadata",
    )
    
    # ============================================
    # Metrics
    # ============================================
    message_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of messages",
    )
    
    user_message_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of user messages",
    )
    
    assistant_message_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of assistant messages",
    )
    
    escalation_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of escalations",
    )
    
    # ============================================
    # Satisfaction
    # ============================================
    satisfaction_score = Column(
        Integer,
        nullable=True,
        comment="User satisfaction score (1-5)",
    )
    
    feedback_text = Column(
        Text,
        nullable=True,
        comment="User feedback",
    )
    
    # ============================================
    # Relationships
    # ============================================
    patient = relationship(
        "Patient",
        back_populates="conversations",
        lazy="joined",
    )
    
    messages = relationship(
        "Message",
        back_populates="conversation",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    escalations = relationship(
        "Escalation",
        back_populates="conversation",
        lazy="selectin",
    )
    
    # ============================================
    # Indexes
    # ============================================
    __table_args__ = (
        Index("idx_conversation_patient", "patient_id"),
        Index("idx_conversation_status", "status"),
        Index("idx_conversation_started", "started_at"),
        Index("idx_conversation_session", "session_token"),
    )
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculate conversation duration in minutes"""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        return (datetime.now(timezone.utc) - self.started_at).total_seconds() / 60
    
    @property
    def is_active(self) -> bool:
        """Check if conversation is active"""
        return self.status == ConversationStatus.ACTIVE
    
    def mark_completed(self) -> None:
        """Mark conversation as completed"""
        self.status = ConversationStatus.COMPLETED
        self.ended_at = datetime.now(timezone.utc)
    
    def mark_escalated(self) -> None:
        """Mark conversation as escalated"""
        self.status = ConversationStatus.ESCALATED
        self.escalation_count += 1
    
    def mark_timeout(self) -> None:
        """Mark conversation as timed out"""
        self.status = ConversationStatus.TIMEOUT
        self.ended_at = datetime.now(timezone.utc)
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity_at = datetime.now(timezone.utc)