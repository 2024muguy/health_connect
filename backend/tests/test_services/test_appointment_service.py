"""
HealthConnect AI - Appointment Service Tests
=============================================
Tests for AppointmentService.
"""

import pytest
from datetime import datetime, timedelta, timezone

from app.services.appointment_service import AppointmentService


class TestAppointmentService:
    """Test appointment service"""
    
    @pytest.fixture
    def service(self):
        """Create appointment service"""
        return AppointmentService()
    
    @pytest.mark.asyncio
    async def test_create_appointment(self, service):
        """Test appointment creation"""
        result = await service.create_appointment(
            patient_id="PAT-TEST",
            appointment_type="general",
            scheduled_datetime=datetime.now(timezone.utc) + timedelta(days=1),
        )
        
        assert result["appointment_code"].startswith("APT-")
        assert result["status"] == "scheduled"
    
    @pytest.mark.asyncio
    async def test_check_availability(self, service):
        """Test availability check"""
        result = await service.check_availability("2024-12-01")
        
        assert result["total_slots"] > 0
        assert len(result["available_slots"]) == result["total_slots"]
    
    @pytest.mark.asyncio
    async def test_cancel_appointment(self, service):
        """Test appointment cancellation"""
        result = await service.cancel_appointment(
            appointment_id="APT-TEST",
            reason="Test cancellation",
        )
        
        assert result["status"] in ["error", "pending_approval"]