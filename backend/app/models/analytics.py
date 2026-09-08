"""
HealthConnect AI - Analytics Model
===================================
Analytics event database model.

Fields:
- Event type and category
- Event data
- User and conversation reference
- Performance metrics
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    Float,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AnalyticsEvent(BaseModel):
    """
    Analytics event model for tracking system events.
    """
    
    __tablename__ = "analytics_events"
    
    # ============================================
    # Event Identification
    # ============================================
    event_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique event code",
    )
    
    event_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Event type (e.g., message_sent, appointment_booked)",
    )
    
    event_category = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Event category (conversation, appointment, safety, performance)",
    )
    
    # ============================================
    # References
    # ============================================
    conversation_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Reference to conversation",
    )
    
    patient_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Reference to patient",
    )
    
    user_id = Column(
        String(100),
        nullable=True,
        comment="User identifier",
    )
    
    # ============================================
    # Event Data
    # ============================================
    data = Column(
        JSON,
        nullable=True,
        comment="Event-specific data",
    )
    
    # ============================================
    # Performance Metrics
    # ============================================
    duration_ms = Column(
        Float,
        nullable=True,
        comment="Event duration in milliseconds",
    )
    
    success = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether event was successful",
    )
    
    error_message = Column(
        String(500),
        nullable=True,
        comment="Error message if failed",
    )
    
    # ============================================
    # Client Information
    # ============================================
    client_ip = Column(
        String(50),
        nullable=True,
        comment="Client IP address",
    )
    
    user_agent = Column(
        String(500),
        nullable=True,
        comment="User agent string",
    )
    
    device_type = Column(
        String(50),
        nullable=True,
        comment="Device type (mobile, desktop, tablet)",
    )
    
    # ============================================
    # Indexes
    # ============================================
    __table_args__ = (
        Index("idx_analytics_type", "event_type"),
        Index("idx_analytics_category", "event_category"),
        Index("idx_analytics_conversation", "conversation_id"),
        Index("idx_analytics_patient", "patient_id"),
        Index("idx_analytics_created", "created_at"),
        Index("idx_analytics_type_created", "event_type", "created_at"),
    )