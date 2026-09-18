"""
HealthConnect AI - Message Model
=================================
Message database model for individual messages.

Fields:
- Message content
- Sender type
- Intent classification
- Safety classification
- Confidence scores
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
    Float,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MessageSender(enum.Enum):
    """Message sender enumeration"""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"


class MessageType(enum.Enum):
    """Message type enumeration"""
    
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    BUTTON = "button"
    CARD = "card"
    QUICK_REPLY = "quick_reply"
    ERROR = "error"
    SYSTEM = "system"


class Message(BaseModel):
    """
    Message model for storing individual messages.
    """
    
    __tablename__ = "messages"
    
    # ============================================
    # Message Identification
    # ============================================
    message_code = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: f"MSG-{uuid.uuid4().hex[:8].upper()}",
        comment="Unique message code (MSG-XXXXXXXX)",
    )
    
    # ============================================
    # Foreign Keys
    # ============================================
    conversation_id = Column(
        String(64),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to conversation",
    )
    
    # ============================================
    # Message Details
    # ============================================
    sender_type = Column(
        Enum(MessageSender, name="message_sender_enum"),
        nullable=False,
        comment="Who sent the message",
    )
    
    message_type = Column(
        Enum(MessageType, name="message_type_enum"),
        default=MessageType.TEXT,
        nullable=False,
        comment="Type of message",
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="Message content",
    )
    
    # ============================================
    # Intent Classification
    # ============================================
    intent = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Classified intent",
    )
    
    intent_confidence = Column(
        Float,
        nullable=True,
        comment="Intent classification confidence (0-1)",
    )
    
    alternative_intents = Column(
        JSON,
        nullable=True,
        comment="Alternative possible intents",
    )
    
    # ============================================
    # Safety Classification
    # ============================================
    safety_category = Column(
        String(50),
        nullable=True,
        comment="Safety classification",
    )
    
    safety_action = Column(
        String(50),
        nullable=True,
        comment="Safety action taken",
    )
    
    safety_score = Column(
        Float,
        nullable=True,
        comment="Safety score (0-1)",
    )
    
    risk_score = Column(
        Integer,
        nullable=True,
        comment="Risk score (0-100)",
    )
    
    # ============================================
    # Retrieved Context
    # ============================================
    retrieved_chunks = Column(
        JSON,
        nullable=True,
        comment="Retrieved knowledge chunks used",
    )
    
    citations = Column(
        JSON,
        nullable=True,
        comment="Source citations",
    )
    
    # ============================================
    # Model Information
    # ============================================
    model_name = Column(
        String(100),
        nullable=True,
        comment="LLM model used for response",
    )
    
    generation_time_ms = Column(
        Float,
        nullable=True,
        comment="Response generation time in milliseconds",
    )
    
    # ============================================
    # Metadata
    # ============================================
    message_model_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional message metadata",
    )
    
    # ============================================
    # Relationships
    # ============================================
    conversation = relationship(
        "Conversation",
        back_populates="messages",
        lazy="joined",
    )
    
    # ============================================
    # Indexes
    # ============================================
    __table_args__ = (
        Index("idx_message_conversation", "conversation_id"),
        Index("idx_message_sender", "sender_type"),
        Index("idx_message_intent", "intent"),
        Index("idx_message_safety", "safety_category"),
        Index("idx_message_created", "created_at"),
    )
    
    @property
    def is_from_user(self) -> bool:
        """Check if message is from user"""
        return self.sender_type == MessageSender.USER
    
    @property
    def is_from_assistant(self) -> bool:
        """Check if message is from assistant"""
        return self.sender_type == MessageSender.ASSISTANT
    
    @property
    def is_blocked(self) -> bool:
        """Check if message was blocked"""
        return self.safety_action == "block"
    
    @property
    def is_emergency(self) -> bool:
        """Check if message triggered emergency protocol"""
        return self.safety_action == "emergency_protocol"