"""
HealthConnect AI - Chat Schemas
================================
Pydantic schemas for chat endpoints.

Schemas:
- ChatRequest: Incoming chat message
- ChatResponse: AI response
- MessageSchema: Message representation
- ConversationSchema: Conversation representation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, validator, ConfigDict


class ChatRequest(BaseModel):
    """Incoming chat message request"""
    
    model_config = ConfigDict(extra="forbid")
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message content",
    )
    
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID for continuing conversation",
    )
    
    session_token: Optional[str] = Field(
        default=None,
        description="Session token for authentication",
    )
    
    patient_id: Optional[str] = Field(
        default=None,
        description="Patient identifier if known",
    )
    
    language: str = Field(
        default="en",
        description="Message language",
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata",
    )
    
    @validator("message")
    def validate_message(cls, v: str) -> str:
        """Validate and clean message"""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        return v
    
    @validator("language")
    def validate_language(cls, v: str) -> str:
        """Validate language code"""
        allowed = {"en", "es", "fr", "de", "zh", "ar", "hi", "pt"}
        if v.lower() not in allowed:
            raise ValueError(f"Unsupported language: {v}")
        return v.lower()


class ChatResponse(BaseModel):
    """AI chat response"""
    
    model_config = ConfigDict(extra="allow")
    
    message_id: UUID = Field(..., description="Message ID")
    conversation_id: UUID = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI response text")
    intent: str = Field(..., description="Detected intent")
    intent_confidence: float = Field(..., ge=0, le=1, description="Intent confidence")
    safety_category: str = Field(..., description="Safety classification")
    safety_score: float = Field(..., ge=0, le=1, description="Safety score")
    action_performed: Optional[Any] = Field(default=None, description="Action performed (string or dict)")
    requires_human: bool = Field(default=False, description="Whether human intervention needed")
    citations: List[Dict[str, str]] = Field(default_factory=list, description="Source citations")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class MessageSchema(BaseModel):
    """Message representation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    conversation_id: UUID
    sender_type: str
    message_type: str = "text"
    content: str
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    safety_category: Optional[str] = None
    safety_action: Optional[str] = None
    safety_score: Optional[float] = None
    created_at: datetime


class ConversationSchema(BaseModel):
    """Conversation representation"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    conversation_code: str
    status: str
    channel: str
    language: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    message_count: int = 0
    escalation_count: int = 0
    satisfaction_score: Optional[int] = None
    summary: Optional[str] = None


class ConversationListResponse(BaseModel):
    """List of conversations"""
    
    conversations: List[ConversationSchema]
    total: int
    page: int
    page_size: int


class FeedbackRequest(BaseModel):
    """User feedback request"""
    
    model_config = ConfigDict(extra="forbid")
    
    conversation_id: UUID = Field(..., description="Conversation ID")
    satisfaction_score: int = Field(..., ge=1, le=5, description="Satisfaction score 1-5")
    feedback_text: Optional[str] = Field(default=None, max_length=1000, description="Feedback text")
    helpful: Optional[bool] = Field(default=None, description="Whether response was helpful")