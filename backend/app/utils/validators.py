"""
HealthConnect AI - Input Validators
====================================
Comprehensive input validation utilities.

Features:
- Email validation
- Phone number validation
- Date/time validation
- Appointment ID validation
- Patient ID validation
- Insurance number validation
- ZIP code validation
"""

import re
from datetime import datetime, date, timedelta
from typing import Optional, Tuple, Any
from email_validator import validate_email as email_validator, EmailNotValidError

from config.logging_config import get_logger

logger = get_logger(__name__)


class ValidationResult:
    """Result of validation operation"""
    
    def __init__(self, is_valid: bool, error_message: Optional[str] = None, normalized_value: Any = None):
        self.is_valid = is_valid
        self.error_message = error_message
        self.normalized_value = normalized_value
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __repr__(self) -> str:
        return f"ValidationResult(is_valid={self.is_valid}, error={self.error_message})"


def validate_email(email: str) -> ValidationResult:
    """
    Validate email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        ValidationResult: Validation result with normalized email
    """
    if not email:
        return ValidationResult(False, "Email is required")
    
    try:
        result = email_validator(email, check_deliverability=False)
        return ValidationResult(True, normalized_value=result.normalized)
    except EmailNotValidError as e:
        return ValidationResult(False, str(e))


def validate_phone(phone: str) -> ValidationResult:
    """
    Validate phone number.
    Accepts formats: +1-555-123-4567, (555) 123-4567, 555-123-4567, 5551234567
    
    Args:
        phone: Phone number to validate
        
    Returns:
        ValidationResult: Validation result with normalized phone
    """
    if not phone:
        return ValidationResult(False, "Phone number is required")
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if has country code
    if cleaned.startswith('+'):
        digits = cleaned[1:]
        if not digits.isdigit():
            return ValidationResult(False, "Invalid phone number format")
    else:
        digits = cleaned
    
    # Validate length (7-15 digits)
    if len(digits) < 7 or len(digits) > 15:
        return ValidationResult(False, "Phone number must be 7-15 digits")
    
    # Format: +X-XXX-XXX-XXXX
    if len(digits) == 10:
        formatted = f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits.startswith('1'):
        formatted = f"+1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
    else:
        formatted = f"+{digits}"
    
    return ValidationResult(True, normalized_value=formatted)


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> ValidationResult:
    """
    Validate date string.
    
    Args:
        date_str: Date string to validate
        format: Expected date format
        
    Returns:
        ValidationResult: Validation result with parsed date
    """
    if not date_str:
        return ValidationResult(False, "Date is required")
    
    try:
        parsed_date = datetime.strptime(date_str, format)
        return ValidationResult(True, normalized_value=parsed_date)
    except ValueError:
        return ValidationResult(False, f"Date must be in format: {format}")


def validate_datetime(datetime_str: str) -> ValidationResult:
    """
    Validate datetime string.
    
    Args:
        datetime_str: Datetime string to validate
        
    Returns:
        ValidationResult: Validation result with parsed datetime
    """
    if not datetime_str:
        return ValidationResult(False, "Datetime is required")
    
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(datetime_str, fmt)
            return ValidationResult(True, normalized_value=parsed)
        except ValueError:
            continue
    
    return ValidationResult(False, "Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")


def validate_appointment_id(appointment_id: str) -> ValidationResult:
    """
    Validate appointment ID.
    Format: APT-XXXXXXXX (8 hex characters)
    
    Args:
        appointment_id: Appointment ID to validate
        
    Returns:
        ValidationResult: Validation result
    """
    if not appointment_id:
        return ValidationResult(False, "Appointment ID is required")
    
    pattern = r'^APT-[A-F0-9]{8}$'
    if re.match(pattern, appointment_id.upper()):
        return ValidationResult(True, normalized_value=appointment_id.upper())
    
    return ValidationResult(False, "Invalid appointment ID format. Expected: APT-XXXXXXXX")


def validate_patient_id(patient_id: str) -> ValidationResult:
    """
    Validate patient ID.
    Format: PAT-XXXXXXXX (8 hex characters)
    
    Args:
        patient_id: Patient ID to validate
        
    Returns:
        ValidationResult: Validation result
    """
    if not patient_id:
        return ValidationResult(False, "Patient ID is required")
    
    pattern = r'^PAT-[A-F0-9]{8}$'
    if re.match(pattern, patient_id.upper()):
        return ValidationResult(True, normalized_value=patient_id.upper())
    
    return ValidationResult(False, "Invalid patient ID format. Expected: PAT-XXXXXXXX")


def validate_name(name: str, field_name: str = "Name") -> ValidationResult:
    """
    Validate person name.
    
    Args:
        name: Name to validate
        field_name: Name of the field for error message
        
    Returns:
        ValidationResult: Validation result
    """
    if not name:
        return ValidationResult(False, f"{field_name} is required")
    
    if len(name) < 2:
        return ValidationResult(False, f"{field_name} must be at least 2 characters")
    
    if len(name) > 100:
        return ValidationResult(False, f"{field_name} must be less than 100 characters")
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r'^[A-Za-z\s\-\']+$', name):
        return ValidationResult(False, f"{field_name} contains invalid characters")
    
    return ValidationResult(True, normalized_value=name.strip())


def validate_insurance_number(insurance_number: str) -> ValidationResult:
    """
    Validate insurance number.
    
    Args:
        insurance_number: Insurance number to validate
        
    Returns:
        ValidationResult: Validation result
    """
    if not insurance_number:
        return ValidationResult(False, "Insurance number is required")
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', insurance_number)
    
    if len(cleaned) < 8 or len(cleaned) > 20:
        return ValidationResult(False, "Insurance number must be 8-20 characters")
    
    if not re.match(r'^[A-Z0-9]+$', cleaned, re.IGNORECASE):
        return ValidationResult(False, "Insurance number can only contain letters and numbers")
    
    return ValidationResult(True, normalized_value=cleaned.upper())


def validate_zip_code(zip_code: str) -> ValidationResult:
    """
    Validate ZIP/postal code.
    
    Args:
        zip_code: ZIP code to validate
        
    Returns:
        ValidationResult: Validation result
    """
    if not zip_code:
        return ValidationResult(False, "ZIP code is required")
    
    # US ZIP code (5 digits or 5+4)
    us_pattern = r'^\d{5}(-\d{4})?$'
    # Canadian postal code
    ca_pattern = r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$'
    # UK postcode
    uk_pattern = r'^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$'
    
    if re.match(us_pattern, zip_code):
        return ValidationResult(True, normalized_value=zip_code)
    elif re.match(ca_pattern, zip_code, re.IGNORECASE):
        return ValidationResult(True, normalized_value=zip_code.upper())
    elif re.match(uk_pattern, zip_code, re.IGNORECASE):
        return ValidationResult(True, normalized_value=zip_code.upper())
    
    return ValidationResult(False, "Invalid ZIP/postal code format")


def validate_positive_number(value: Any, field_name: str = "Value") -> ValidationResult:
    """
    Validate positive number.
    
    Args:
        value: Value to validate
        field_name: Field name for error message
        
    Returns:
        ValidationResult: Validation result
    """
    try:
        num = float(value)
        if num <= 0:
            return ValidationResult(False, f"{field_name} must be positive")
        return ValidationResult(True, normalized_value=num)
    except (ValueError, TypeError):
        return ValidationResult(False, f"{field_name} must be a number")


def validate_age(age: int) -> ValidationResult:
    """
    Validate age.
    
    Args:
        age: Age to validate
        
    Returns:
        ValidationResult: Validation result
    """
    try:
        age_int = int(age)
        if age_int < 0 or age_int > 150:
            return ValidationResult(False, "Age must be between 0 and 150")
        return ValidationResult(True, normalized_value=age_int)
    except (ValueError, TypeError):
        return ValidationResult(False, "Age must be a number")


def validate_appointment_time(
    appointment_datetime: datetime,
    business_hours: Tuple[int, int] = (8, 18),
) -> ValidationResult:
    """
    Validate appointment time is within business hours.
    
    Args:
        appointment_datetime: Appointment datetime
        business_hours: (start_hour, end_hour)
        
    Returns:
        ValidationResult: Validation result
    """
    start_hour, end_hour = business_hours
    
    if appointment_datetime.hour < start_hour or appointment_datetime.hour >= end_hour:
        return ValidationResult(
            False,
            f"Appointment must be between {start_hour}:00 and {end_hour}:00"
        )
    
    # Check if weekend (Saturday=5, Sunday=6)
    if appointment_datetime.weekday() >= 5:
        return ValidationResult(False, "Appointments are only available Monday-Friday")
    
    return ValidationResult(True)


def validate_future_date(dt: datetime) -> ValidationResult:
    """
    Validate datetime is in the future.
    
    Args:
        dt: Datetime to validate
        
    Returns:
        ValidationResult: Validation result
    """
    if dt <= datetime.now():
        return ValidationResult(False, "Date must be in the future")
    
    return ValidationResult(True)