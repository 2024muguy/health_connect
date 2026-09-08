"""
HealthConnect AI - Appointment Schemas
=======================================
Pydantic schemas for appointment endpoints.

Schemas:
- AppointmentCreate
- AppointmentUpdate
- AppointmentResponse
- AppointmentCancelRequest
- AppointmentRescheduleRequest
"""

from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, Field, validator, ConfigDict

from app.models.appointment import AppointmentStatus, AppointmentType


class AppointmentCreate(BaseModel):
    """Create appointment request"""
    
    model_config = ConfigDict(extra="forbid")
    
    patient_id: UUID = Field(..., description="Patient ID")
    appointment_type: AppointmentType = Field(..., description="Type of appointment")
    scheduled_datetime: datetime = Field(..., description="Scheduled datetime")
    duration_minutes: int = Field(default=30, ge=10, le=120, description="Duration in minutes")
    reason: Optional[str] = Field(default=None, max_length=500, description="Reason for appointment")
    clinic_location: Optional[str] = Field(default=None, description="Clinic location")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Additional notes")
    
    @validator("scheduled_datetime")
    def validate_scheduled_datetime(cls, v: datetime) -> datetime:
        """Validate appointment is in the future"""
        if v <= datetime.now(v.tzinfo):
            raise ValueError("Appointment must be in the future")
        
        # Validate business hours (8 AM - 6 PM)
        if v.hour < 8 or v.hour >= 18:
            raise ValueError("Appointment must be between 8:00 AM and 6:00 PM")
        
        # Validate not weekend
        if v.weekday() >= 5:
            raise ValueError("Appointment must be on a weekday")
        
        return v


class AppointmentUpdate(BaseModel):
    """Update appointment request"""
    
    model_config = ConfigDict(extra="forbid")
    
    appointment_type: Optional[AppointmentType] = None
    scheduled_datetime: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=10, le=120)
    reason: Optional[str] = Field(default=None, max_length=500)
    clinic_location: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[AppointmentStatus] = None


class AppointmentRescheduleRequest(BaseModel):
    """Reschedule appointment request"""
    
    model_config = ConfigDict(extra="forbid")
    
    appointment_id: UUID = Field(..., description="Appointment ID to reschedule")
    new_datetime: datetime = Field(..., description="New scheduled datetime")
    reason: Optional[str] = Field(default=None, max_length=500, description="Reason for rescheduling")
    
    @validator("new_datetime")
    def validate_new_datetime(cls, v: datetime) -> datetime:
        """Validate new datetime"""
        if v <= datetime.now(v.tzinfo):
            raise ValueError("New datetime must be in the future")
        
        if v.hour < 8 or v.hour >= 18:
            raise ValueError("Appointment must be between 8:00 AM and 6:00 PM")
        
        if v.weekday() >= 5:
            raise ValueError("Appointment must be on a weekday")
        
        return v


class AppointmentCancelRequest(BaseModel):
    """Cancel appointment request"""
    
    model_config = ConfigDict(extra="forbid")
    
    appointment_id: UUID = Field(..., description="Appointment ID to cancel")
    reason: Optional[str] = Field(default=None, max_length=500, description="Cancellation reason")
    confirm_cancellation: bool = Field(
        default=False,
        description="Explicit confirmation of cancellation",
    )
    
    @validator("confirm_cancellation")
    def validate_confirmation(cls, v: bool) -> bool:
        """Validate cancellation is confirmed"""
        if not v:
            raise ValueError("Cancellation must be explicitly confirmed")
        return v


class AppointmentResponse(BaseModel):
    """Appointment response"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    appointment_code: str
    patient_id: UUID
    appointment_type: str
    status: str
    scheduled_datetime: datetime
    duration_minutes: int
    reason: Optional[str] = None
    clinic_location: Optional[str] = None
    reminder_sent: bool = False
    no_show: bool = False
    created_at: datetime
    updated_at: datetime


class AppointmentListResponse(BaseModel):
    """List of appointments"""
    
    appointments: List[AppointmentResponse]
    total: int
    page: int
    page_size: int