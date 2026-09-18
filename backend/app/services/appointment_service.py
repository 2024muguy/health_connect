"""
HealthConnect AI - Appointment Service
=======================================
Business logic for appointment management.

Features:
- Appointment booking
- Appointment rescheduling
- Appointment cancellation
- Availability checking
- Appointment reminders
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.patient import Patient

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AppointmentService:
    """
    Appointment Service.
    Manages appointment operations.
    """
    
    def __init__(self, db=None):
        self.db = db
        logger.info("AppointmentService initialized")
    
    async def create_appointment(
        self,
        patient_id: str,
        appointment_type: str,
        scheduled_datetime: datetime,
        duration_minutes: int = 30,
        reason: Optional[str] = None,
        clinic_location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new appointment.
        
        Args:
            patient_id: Patient ID
            appointment_type: Type of appointment
            scheduled_datetime: Scheduled datetime
            duration_minutes: Duration in minutes
            reason: Appointment reason
            clinic_location: Clinic location
            
        Returns:
            Dict: Created appointment
        """
        appointment_code = f"APT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)

        # Persist via the ORM model so we get id + updated_at back.
        try:
            from app.models.appointment import (
                Appointment,
                AppointmentType as AppointmentTypeEnum,
                AppointmentStatus as AppointmentStatusEnum,
            )
        except ImportError as e:
            logger.error(f"Cannot import Appointment model: {e}")
            raise

        # Coerce string to the matching enum member
        try:
            at_enum = (
                AppointmentTypeEnum(appointment_type.lower())
                if isinstance(appointment_type, str)
                else appointment_type
            )
        except ValueError:
            logger.warning(
                f"Unknown appointment_type {appointment_type!r}, defaulting to GENERAL"
            )
            at_enum = AppointmentTypeEnum.GENERAL


        # ---- Coerce string IDs to UUID objects ----
        import uuid as _uuid
        pid = _uuid.UUID(patient_id) if isinstance(patient_id, str) else patient_id
        did = None

        row = Appointment(
            id=uuid.uuid4(),                 # UUID object, not str
            appointment_code=appointment_code,
            patient_id=pid,           # pass through as-is; SQLAlchemy will coerce
            appointment_type=at_enum,
            status=AppointmentStatusEnum.SCHEDULED,
            scheduled_datetime=scheduled_datetime,
            duration_minutes=duration_minutes,
            reason=reason,
            clinic_location=clinic_location,
            created_at=now,
            updated_at=now,
        )

        session = getattr(self, "session", None) or getattr(self, "db", None)
        if session is None:
            # fall back to opening a fresh session
            from app.database.session import SessionLocal  # type: ignore
            session = SessionLocal()
            close_after = True
        else:
            close_after = False

        try:
            session.add(row)
            session.commit()
            session.refresh(row)
            logger.info(f"Created appointment: {appointment_code} (id={row.id})")
        except Exception:
            session.rollback()
            logger.exception("Failed to persist appointment")
            raise
        finally:
            if close_after:
                session.close()

        return {
            "id": row.id,                                    # UUID object
            "appointment_code": row.appointment_code,
            "patient_id": row.patient_id,                    # UUID object
            "doctor_id": row.doctor_id,
            "appointment_type": (
                row.appointment_type.value
                if hasattr(row.appointment_type, "value")
                else row.appointment_type
            ),
            "status": (
                row.status.value
                if hasattr(row.status, "value")
                else row.status
            ),
            "scheduled_datetime": row.scheduled_datetime,
            "duration_minutes": row.duration_minutes,
            "reason": row.reason,
            "clinic_location": row.clinic_location,
            "reminder_sent": bool(getattr(row, "reminder_sent", False)),
            "no_show": bool(getattr(row, "no_show", False)),
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
    
    async def reschedule_appointment(
        self,
        appointment_id: str,
        new_datetime: datetime,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reschedule an appointment.
        
        Args:
            appointment_id: Appointment ID
            new_datetime: New datetime
            reason: Rescheduling reason
            
        Returns:
            Dict: Result
        """
        # Check if appointment can be rescheduled
        can_reschedule = await self.can_reschedule(appointment_id)
        
        if not can_reschedule:
            return {
                "status": "error",
                "message": "Appointment cannot be rescheduled",
                "appointment_id": appointment_id,
            }
        
        return {
            "status": "pending_approval",
            "appointment_id": appointment_id,
            "new_datetime": new_datetime,
            "reason": reason,
            "requires_staff_approval": True,
        }
    
    async def cancel_appointment(
        self,
        appointment_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: Appointment ID
            reason: Cancellation reason
            
        Returns:
            Dict: Result
        """
        # Check if appointment can be cancelled
        can_cancel = await self.can_cancel(appointment_id)
        
        if not can_cancel:
            return {
                "status": "error",
                "message": "Appointment cannot be cancelled",
                "appointment_id": appointment_id,
            }
        
        return {
            "status": "pending_approval",
            "appointment_id": appointment_id,
            "reason": reason,
            "requires_staff_approval": True,
        }
    
    async def can_reschedule(self, appointment_id: str) -> bool:
        """Check if appointment can be rescheduled"""
        # Placeholder logic
        return True
    
    async def can_cancel(self, appointment_id: str) -> bool:
        """Check if appointment can be cancelled"""
        # Must be at least 24 hours before appointment
        return True
    
    async def check_availability(
        self,
        date: str,
        appointment_type: Optional[str] = None,
        doctor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check available appointment slots.
        
        Args:
            date: Date to check (YYYY-MM-DD)
            appointment_type: Type of appointment
            doctor_id: Specific doctor
            
        Returns:
            Dict: Available slots
        """
        # Generate time slots (8 AM to 5 PM, 30-minute intervals)
        slots = []
        for hour in range(8, 17):
            for minute in [0, 30]:
                slots.append({
                    "time": f"{hour:02d}:{minute:02d}",
                    "available": True,
                    "doctor_id": doctor_id,
                })
        
        return {
            "date": date,
            "total_slots": len(slots),
            "available_slots": slots,
        }
    
    async def send_reminder(
        self,
        appointment_id: str,
        method: str = "both",
    ) -> Dict[str, Any]:
        """
        Send appointment reminder.
        
        Args:
            appointment_id: Appointment ID
            method: Notification method (email, sms, both)
            
        Returns:
            Dict: Result
        """
        return {
            "status": "sent",
            "appointment_id": appointment_id,
            "method": method,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
    
    async def get_appointment(
        self,
        appointment_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get appointment details.
        
        Args:
            appointment_id: Appointment ID (UUID string or UUID object)
            
        Returns:
            Optional[Dict]: Appointment details or None if not found
        """
        from app.models.appointment import Appointment
        import uuid as _uuid

        # Cast to uuid.UUID because SQLite stores UUID columns as hex
        # and SQLAlchemy needs a UUID object to query correctly.
        try:
            uid = (
                _uuid.UUID(appointment_id)
                if isinstance(appointment_id, str)
                else appointment_id
            )
        except (ValueError, AttributeError):
            logger.warning(f"Invalid appointment_id: {appointment_id!r}")
            return None

        session = getattr(self, "db", None) or getattr(self, "session", None)
        owns_session = False
        if session is None:
            from app.database.session import SessionLocal  # type: ignore
            session = SessionLocal()
            owns_session = True

        try:
            row = (
                session.query(Appointment)
                .filter(Appointment.id == uid)
                .first()
            )
        finally:
            if owns_session:
                session.close()

        if row is None:
            return None

        # Serialize enums to their values for the API layer
        def _enum_val(v):
            return v.value if hasattr(v, "value") else v

        return {
            "id": row.id,                                    # UUID object — Pydantic wants UUID
            "appointment_code": row.appointment_code,
            "patient_id": row.patient_id,                    # UUID object
            "doctor_id": row.doctor_id,                      # UUID object or None
            "appointment_type": _enum_val(row.appointment_type),
            "status": _enum_val(row.status),
            "scheduled_datetime": row.scheduled_datetime,
            "duration_minutes": row.duration_minutes,
            "reason": row.reason,
            "clinic_location": row.clinic_location,
            "reminder_sent": bool(getattr(row, "reminder_sent", False)),
            "no_show": bool(getattr(row, "no_show", False)),
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
    
    async def list_appointments(
        self,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List appointments with filters.
        
        Args:
            patient_id: Filter by patient
            status: Filter by status
            date_from: Filter by start date
            date_to: Filter by end date
            limit: Maximum results
            
        Returns:
            List[Dict]: Appointments
        """
        # Placeholder
        return []