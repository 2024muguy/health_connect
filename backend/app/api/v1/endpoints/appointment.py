"""
HealthConnect AI - Appointment Endpoints
=========================================
Appointment management endpoints.

Endpoints:
- POST /appointments: Create appointment
- GET /appointments: List appointments
- GET /appointments/{id}: Get appointment
- PUT /appointments/{id}: Update appointment
- POST /appointments/{id}/reschedule: Reschedule
- POST /appointments/{id}/cancel: Cancel
- GET /appointments/availability: Check availability
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_appointment_service, get_current_user
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse,
    AppointmentRescheduleRequest,
    AppointmentCancelRequest,
)

from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    request: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    appointment_service = Depends(get_appointment_service),
):
    """
    Create a new appointment.
    """
    result = await appointment_service.create_appointment(
        patient_id=request.patient_id,   # UUID object, not str
        appointment_type=request.appointment_type.value,
        scheduled_datetime=request.scheduled_datetime,
        duration_minutes=request.duration_minutes,
        reason=request.reason,
        clinic_location=request.clinic_location,
    )
    
    return result


@router.get("", response_model=AppointmentListResponse)
async def list_appointments(
    patient_id: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100),
    current_user: dict = Depends(get_current_user),
    appointment_service = Depends(get_appointment_service),
):
    """
    List appointments with filters.
    """
    appointments = await appointment_service.list_appointments(
        patient_id=patient_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )
    
    return AppointmentListResponse(
        appointments=appointments,
        total=len(appointments),
        page=1,
        page_size=limit,
    )


@router.get("/availability")
async def check_availability(
    date: str = Query(..., description="Date (YYYY-MM-DD)"),
    appointment_type: Optional[str] = Query(default=None),
    doctor_id: Optional[str] = Query(default=None),
    current_user: Optional[dict] = Depends(get_current_user),
    appointment_service = Depends(get_appointment_service),
):
    """
    Check appointment availability.
    """
    return await appointment_service.check_availability(
        date=date,
        appointment_type=appointment_type,
        doctor_id=doctor_id,
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user),
    appointment_service = Depends(get_appointment_service),
):
    """
    Get appointment details.
    """
    appointment = await appointment_service.get_appointment(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    request: AppointmentUpdate,
    current_user: dict = Depends(get_current_user),
    appointment_service = Depends(get_appointment_service),
):
    """
    Update appointment.
    """
    return {
        "appointment_id": appointment_id,
        "status": "updated",
        **request.dict(exclude_unset=True),
    }


@router.post("/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: str,
    request: AppointmentRescheduleRequest,
    current_user: dict = Depends(get_current_user),
    appointment_service = Depends(get_appointment_service),
):
    """
    Reschedule appointment.
    """
    result = await appointment_service.reschedule_appointment(
        appointment_id=appointment_id,
        new_datetime=request.new_datetime,
        reason=request.reason,
    )
    
    return result


@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: str,
    request: AppointmentCancelRequest,
    current_user: dict = Depends(get_current_user),
    appointment_service = Depends(get_appointment_service),
):
    """
    Cancel appointment.
    """
    result = await appointment_service.cancel_appointment(
        appointment_id=appointment_id,
        reason=request.reason,
    )
    
    return result