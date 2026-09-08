"""
HealthConnect AI - Admin Schemas
=================================
Pydantic schemas for admin endpoints.

Schemas:
- AdminStats
- AdminUserCreate
- AdminUserResponse
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field, validator, EmailStr, ConfigDict


class AdminStats(BaseModel):
    """Admin dashboard statistics"""
    
    total_patients: int = Field(..., description="Total patients registered")
    total_appointments: int = Field(..., description="Total appointments")
    total_conversations: int = Field(..., description="Total conversations")
    total_escalations: int = Field(..., description="Total escalations")
    pending_escalations: int = Field(..., description="Pending escalations")
    critical_escalations: int = Field(..., description="Critical escalations")
    no_show_rate: float = Field(..., description="No-show rate percentage")
    average_response_time_ms: float = Field(..., description="Average response time")
    average_satisfaction: float = Field(..., description="Average satisfaction score")
    active_conversations: int = Field(..., description="Active conversations")
    appointments_today: int = Field(..., description="Appointments today")
    appointments_this_week: int = Field(..., description="Appointments this week")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_patients": 1250,
                "total_appointments": 5000,
                "total_conversations": 3500,
                "total_escalations": 150,
                "pending_escalations": 25,
                "critical_escalations": 3,
                "no_show_rate": 12.5,
                "average_response_time_ms": 850,
                "average_satisfaction": 4.3,
                "active_conversations": 15,
                "appointments_today": 45,
                "appointments_this_week": 250,
            }
        }


class AdminUserCreate(BaseModel):
    """Create admin user request"""
    
    model_config = ConfigDict(extra="forbid")
    
    email: EmailStr = Field(..., description="Admin email")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    full_name: str = Field(..., min_length=2, max_length=200, description="Full name")
    role: str = Field(default="admin", description="User role")
    department: Optional[str] = Field(default=None, description="Department")
    
    @validator("password")
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class AdminUserResponse(BaseModel):
    """Admin user response"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    full_name: str
    role: str
    department: Optional[str] = None
    is_active: bool = True
    created_at: datetime