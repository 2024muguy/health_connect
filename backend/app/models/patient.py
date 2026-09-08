"""
HealthConnect AI - Patient Model
=================================
Patient database model.

Fields:
- Basic information (name, DOB, contact)
- Insurance information
- Communication preferences
- Appointment history
"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
    Enum,
    ForeignKey,
    Integer,
    Float,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, SoftDeleteMixin


class Patient(BaseModel, SoftDeleteMixin):
    """
    Patient model for storing patient information.
    """
    
    __tablename__ = "patients"
    
    # ============================================
    # Basic Information
    # ============================================
    patient_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique patient code (PAT-XXXXXXXX)",
    )
    
    first_name = Column(
        String(100),
        nullable=False,
        comment="Patient first name",
    )
    
    last_name = Column(
        String(100),
        nullable=False,
        comment="Patient last name",
    )
    
    date_of_birth = Column(
        Date,
        nullable=False,
        comment="Patient date of birth",
    )
    
    gender = Column(
        Enum("male", "female", "other", "prefer_not_to_say", name="gender_enum"),
        nullable=True,
        comment="Patient gender",
    )
    
    # ============================================
    # Contact Information
    # ============================================
    email = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Patient email address",
    )
    
    phone_number = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Patient phone number",
    )
    
    address_line1 = Column(
        String(255),
        nullable=True,
        comment="Address line 1",
    )
    
    address_line2 = Column(
        String(255),
        nullable=True,
        comment="Address line 2",
    )
    
    city = Column(
        String(100),
        nullable=True,
        comment="City",
    )
    
    state = Column(
        String(100),
        nullable=True,
        comment="State/Province",
    )
    
    zip_code = Column(
        String(20),
        nullable=True,
        comment="ZIP/Postal code",
    )
    
    country = Column(
        String(100),
        default="USA",
        nullable=True,
        comment="Country",
    )
    
    # ============================================
    # Insurance Information
    # ============================================
    insurance_provider = Column(
        String(100),
        nullable=True,
        comment="Insurance provider name",
    )
    
    insurance_number = Column(
        String(50),
        nullable=True,
        comment="Insurance policy number",
    )
    
    insurance_group = Column(
        String(50),
        nullable=True,
        comment="Insurance group number",
    )
    
    # ============================================
    # Communication Preferences
    # ============================================
    email_reminders = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether to send email reminders",
    )
    
    sms_reminders = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether to send SMS reminders",
    )
    
    preferred_language = Column(
        String(20),
        default="en",
        nullable=False,
        comment="Preferred communication language",
    )
    
    # ============================================
    # Emergency Contact
    # ============================================
    emergency_contact_name = Column(
        String(200),
        nullable=True,
        comment="Emergency contact name",
    )
    
    emergency_contact_phone = Column(
        String(20),
        nullable=True,
        comment="Emergency contact phone",
    )
    
    emergency_contact_relationship = Column(
        String(50),
        nullable=True,
        comment="Emergency contact relationship",
    )
    
    # ============================================
    # Relationships
    # ============================================
    appointments = relationship(
        "Appointment",
        back_populates="patient",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    conversations = relationship(
        "Conversation",
        back_populates="patient",
        lazy="selectin",
    )
    
    # ============================================
    # Indexes
    # ============================================
    __table_args__ = (
        Index("idx_patient_name", "first_name", "last_name"),
        Index("idx_patient_email", "email"),
        Index("idx_patient_phone", "phone_number"),
        Index("idx_patient_dob", "date_of_birth"),
        UniqueConstraint("email", name="uq_patient_email"),
    )
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return 0
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age
    
    @property
    def has_insurance(self) -> bool:
        """Check if patient has insurance"""
        return bool(self.insurance_provider and self.insurance_number)
    
    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """Override to_dict to include full_name and age"""
        exclude = exclude or []
        result = super().to_dict(exclude)
        result["full_name"] = self.full_name
        result["age"] = self.age
        return result