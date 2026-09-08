"""
HealthConnect AI - Analytics Schemas
=====================================
Pydantic schemas for analytics endpoints.

Schemas:
- AnalyticsEventCreate
- AnalyticsEventResponse
- AnalyticsReport
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class AnalyticsEventCreate(BaseModel):
    """Create analytics event"""
    
    model_config = ConfigDict(extra="forbid")
    
    event_type: str = Field(..., min_length=1, max_length=100, description="Event type")
    event_category: str = Field(..., min_length=1, max_length=50, description="Event category")
    conversation_id: Optional[UUID] = Field(default=None, description="Conversation ID")
    patient_id: Optional[UUID] = Field(default=None, description="Patient ID")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Event data")
    duration_ms: Optional[float] = Field(default=None, ge=0, description="Duration in milliseconds")
    success: bool = Field(default=True, description="Whether event was successful")
    error_message: Optional[str] = Field(default=None, max_length=500, description="Error message")
    client_ip: Optional[str] = Field(default=None, description="Client IP")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    device_type: Optional[str] = Field(default=None, description="Device type")


class AnalyticsEventResponse(BaseModel):
    """Analytics event response"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    event_code: str
    event_type: str
    event_category: str
    conversation_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None
    data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    success: bool = True
    created_at: datetime


class AnalyticsReport(BaseModel):
    """Analytics report"""
    
    report_date: date = Field(..., description="Report date")
    total_conversations: int = Field(..., description="Total conversations")
    total_messages: int = Field(..., description="Total messages")
    average_response_time_ms: float = Field(..., description="Average response time")
    average_satisfaction: float = Field(..., description="Average satisfaction")
    no_show_rate: float = Field(..., description="No-show rate")
    escalation_rate: float = Field(..., description="Escalation rate")
    containment_rate: float = Field(..., description="Containment rate")
    safety_violations: int = Field(..., description="Safety violations")
    top_intents: List[Dict[str, Any]] = Field(default_factory=list, description="Top intents")
    top_concerns: List[Dict[str, Any]] = Field(default_factory=list, description="Top patient concerns")
    hourly_activity: Dict[str, int] = Field(default_factory=dict, description="Hourly activity counts")