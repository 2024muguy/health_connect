"""
HealthConnect AI - User Model
==============================
Authentication and user profile persistence.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column, String, DateTime, Boolean, Index, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """
    User account.
    Persists to whichever DB is configured (SQLite or Neon Postgres).
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        {"extend_existing": True}
    )

    # Primary key
    id = Column(String(64), primary_key=True, default=lambda: f"USR-{uuid.uuid4().hex[:8].upper()}")

    # Credentials
    email = Column(String(320), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    roles = Column(String(200), nullable=False, default="user")  # comma-separated

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "roles": (self.roles or "user").split(","),
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
