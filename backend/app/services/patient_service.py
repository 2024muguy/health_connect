"""
HealthConnect AI - Patient Service
==================================
Ensures every authenticated user has a matching patient profile (1:1).
No duplicates. Idempotent.
"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.user import User
from config.logging_config import get_logger

logger = get_logger(__name__)


def _generate_patient_code() -> str:
    return f"PAT-{uuid.uuid4().hex[:8].upper()}"


def _split_name(full_name: str) -> tuple[str, str]:
    parts = (full_name or "Unknown User").strip().split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], "."
    return parts[0], parts[1]


def ensure_patient_profile(db: Session, user: User) -> Patient:
    """
    Return the Patient row linked to `user`, creating it if missing.
    Safe to call repeatedly — idempotent by user_id.
    """
    existing = db.query(Patient).filter(Patient.user_id == user.id).first()
    if existing:
        return existing

    first, last = _split_name(user.full_name)
    patient = Patient(
        id=uuid.uuid4(),               # UUID object, NOT a string
        user_id=user.id,
        patient_code=_generate_patient_code(),
        first_name=first,
        last_name=last,
        date_of_birth=date(1990, 1, 1),   # placeholder; patient updates profile later
        email=user.email,
        phone_number=getattr(user, "phone", None),
        preferred_language="en",
        email_reminders=True,
        sms_reminders=True,
    )
    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
        logger.info(f"Auto-provisioned patient profile {patient.id} for user {user.id}")
        return patient
    except Exception:
        db.rollback()
        logger.exception("Failed to auto-provision patient profile")
        raise
