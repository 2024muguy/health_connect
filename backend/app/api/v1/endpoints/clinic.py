"""
HealthConnect AI - Clinic Endpoints
====================================
Clinic information endpoints.

Endpoints:
- GET /clinic/info: Get clinic information
- GET /clinic/locations: Get locations
- GET /clinic/services: Get services
- GET /clinic/hours: Get operating hours
"""

from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_optional_user

from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Clinic information (would be loaded from Knowledge Base)
CLINIC_INFO = {
    "name": "HealthConnect Clinic",
    "description": "Comprehensive healthcare services for the community",
    "founded": 2010,
    "locations": [
        {
            "id": "downtown",
            "name": "Downtown Medical Center",
            "address": "123 Main Street, Suite 100",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "phone": "(555) 123-4567",
            "hours": {
                "monday": "8:00 AM - 6:00 PM",
                "tuesday": "8:00 AM - 6:00 PM",
                "wednesday": "8:00 AM - 6:00 PM",
                "thursday": "8:00 AM - 6:00 PM",
                "friday": "8:00 AM - 5:00 PM",
                "saturday": "9:00 AM - 1:00 PM",
                "sunday": "Closed",
            },
        },
        {
            "id": "westside",
            "name": "Westside Family Clinic",
            "address": "456 Oak Avenue",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62704",
            "phone": "(555) 987-6543",
            "hours": {
                "monday": "8:30 AM - 5:30 PM",
                "tuesday": "8:30 AM - 5:30 PM",
                "wednesday": "8:30 AM - 5:30 PM",
                "thursday": "8:30 AM - 5:30 PM",
                "friday": "8:30 AM - 4:30 PM",
                "saturday": "Closed",
                "sunday": "Closed",
            },
        },
    ],
    "services": [
        "Primary Care",
        "Pediatrics",
        "Internal Medicine",
        "Dermatology",
        "Cardiology",
        "Orthopedics",
        "Laboratory Services",
        "Imaging Services",
        "Vaccinations",
        "Physical Therapy",
    ],
    "insurance_accepted": [
        "Blue Cross Blue Shield",
        "Aetna",
        "Cigna",
        "UnitedHealthcare",
        "Medicare",
        "Medicaid",
        "Humana",
    ],
}


@router.get("/info")
async def get_clinic_info(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Get general clinic information.
    """
    return {
        "name": CLINIC_INFO["name"],
        "description": CLINIC_INFO["description"],
        "founded": CLINIC_INFO["founded"],
    }


@router.get("/locations")
async def get_locations(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Get clinic locations.
    """
    return {
        "locations": CLINIC_INFO["locations"],
        "total": len(CLINIC_INFO["locations"]),
    }


@router.get("/services")
async def get_services(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Get available services.
    """
    return {
        "services": CLINIC_INFO["services"],
        "total": len(CLINIC_INFO["services"]),
    }


@router.get("/hours")
async def get_hours(
    location_id: Optional[str] = Query(default=None),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Get operating hours.
    """
    for location in CLINIC_INFO["locations"]:
        if location["id"] == location_id:
            return {
                "location": location["name"],
                "hours": location["hours"],
            }
    
    # Return all hours if no specific location
    return {
        "locations": [
            {"name": loc["name"], "hours": loc["hours"]}
            for loc in CLINIC_INFO["locations"]
        ]
    }


@router.get("/insurance")
async def get_insurance(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Get accepted insurance providers.
    """
    return {
        "insurance_providers": CLINIC_INFO["insurance_accepted"],
        "total": len(CLINIC_INFO["insurance_accepted"]),
    }