"""
HealthConnect AI - Escalation Schemas
======================================
Pydantic schemas for escalation endpoints.

Schemas:
- EscalationCreate
- EscalationUpdate
- EscalationResponse
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, validator, ConfigDict

from app.models.escalation import EscalationStatus, EscalationTier, EscalationType


class EscalationCreate(BaseModel):
    """Create escalation request"""
    
    model_config = ConfigDict(extra="forbid")
    
    conversation_id: Optional[UUID] = Field(default=None, description="Conversation ID")
    patient_id: Optional[UUID] = Field(default=None, description="Patient ID")
    escalation_type: EscalationType = Field(..., description="Type of escalation")
    tier: EscalationTier = Field(..., description="Escalation tier")
    priority: str = Field(default="normal", description="Priority level")
    department: Optional[str] = Field(default=None, description="Target department")
    reason: str = Field(..., min_length=5, max_length=1000, description="Escalation reason")
    description: Optional[str] = Field(default=None, max_length=2000, description="Detailed description")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Conversation context")
    
    @validator("priority")
    def validate_priority(cls, v: str) -> str:
        """Validate priority value"""
        allowed = {"low", "normal", "high", "critical"}
        if v.lower() not in allowed:
            raise ValueError(f"Priority must be one of: {allowed}")
        return v.lower()


class EscalationUpdate(BaseModel):
    """Update escalation request"""
    
    model_config = ConfigDict(extra="forbid")
    
    status: Optional[EscalationStatus] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    priority: Optional[str] = None
    department: Optional[str] = None


class EscalationResponse(BaseModel):
    """Escalation response"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    escalation_code: str
    conversation_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None
    escalation_type: str
    tier: str
    status: str
    priority: str
    department: Optional[str] = None
    reason: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class EscalationListResponse(BaseModel):
    """List of escalations"""
    
    escalations: List[EscalationResponse]
    total: int
    page: int
    page_size: int
    pending_count: int
    critical_count: int