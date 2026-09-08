"""
HealthConnect AI - Webhook Endpoints
=====================================
External webhook endpoints for integrations.

Endpoints:
- POST /webhooks/appointment: Appointment webhook
- POST /webhooks/notification: Notification webhook
- POST /webhooks/patient: Patient webhook
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import hmac
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header

from app.api.deps import get_notification_service, get_audit_service

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


async def verify_webhook_signature(
    request: Request,
    x_signature: Optional[str] = Header(default=None),
) -> bool:
    """
    Verify webhook signature.
    
    Args:
        request: Request object
        x_signature: Signature header
        
    Returns:
        bool: True if signature is valid
    """
    if not x_signature:
        return False
    
    body = await request.body()
    
    # Create HMAC signature
    expected_signature = hmac.new(
        settings.SECRET_KEY.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, x_signature)


@router.post("/appointment")
async def appointment_webhook(
    request: Request,
    notification_service = Depends(get_notification_service),
    audit_service = Depends(get_audit_service),
):
    """
    Handle appointment webhook from external systems.
    """
    # Verify signature
    signature_valid = await verify_webhook_signature(
        request,
        request.headers.get("X-Signature"),
    )
    
    if not signature_valid:
        await audit_service.log_event(
            event_type="webhook_signature_failure",
            severity="warning",
            details={"endpoint": "appointment"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )
    
    # Parse webhook payload
    payload = await request.json()
    
    event_type = payload.get("event_type", "unknown")
    appointment_data = payload.get("appointment", {})
    
    logger.info(f"Received appointment webhook: {event_type}")
    
    # Log webhook
    await audit_service.log_event(
        event_type=f"webhook_appointment_{event_type}",
        severity="info",
        details=appointment_data,
    )
    
    # Process based on event type
    if event_type == "appointment_confirmed":
        # Send confirmation notification
        if appointment_data.get("patient_email"):
            await notification_service.send_appointment_confirmation(
                patient_email=appointment_data["patient_email"],
                patient_name=appointment_data.get("patient_name", "Patient"),
                appointment_datetime=appointment_data.get("scheduled_datetime", ""),
                clinic_location=appointment_data.get("clinic_location", "HealthConnect Clinic"),
            )
    
    return {"status": "processed", "event_type": event_type}


@router.post("/notification")
async def notification_webhook(
    request: Request,
    notification_service = Depends(get_notification_service),
    audit_service = Depends(get_audit_service),
):
    """
    Handle notification webhook from notification services.
    """
    payload = await request.json()
    
    notification_type = payload.get("type", "unknown")
    recipient = payload.get("recipient", "")
    
    logger.info(f"Received notification webhook: {notification_type}")
    
    await audit_service.log_event(
        event_type=f"webhook_notification_{notification_type}",
        severity="info",
        details={"recipient": recipient},
    )
    
    return {"status": "logged", "type": notification_type}


@router.post("/patient")
async def patient_webhook(
    request: Request,
    audit_service = Depends(get_audit_service),
):
    """
    Handle patient webhook from external systems.
    """
    payload = await request.json()
    
    event_type = payload.get("event_type", "unknown")
    patient_data = payload.get("patient", {})
    
    logger.info(f"Received patient webhook: {event_type}")
    
    await audit_service.log_event(
        event_type=f"webhook_patient_{event_type}",
        severity="info",
        details={"patient_id": patient_data.get("patient_id", "unknown")},
    )
    
    return {"status": "processed", "event_type": event_type}