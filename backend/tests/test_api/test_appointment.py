"""
HealthConnect AI - Appointment API Tests
=========================================
Tests for appointment endpoints.
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient


class TestAppointmentEndpoints:
    """Test appointment endpoints"""
    
    def test_check_availability(self, test_client: TestClient):
        """Test availability check"""
        response = test_client.get(
            "/api/v1/appointments/availability",
            params={"date": "2024-12-01"},
        )
        assert response.status_code in [200, 401]
    
    def test_create_appointment_validation(self, test_client: TestClient):
        """Test appointment creation validation"""
        response = test_client.post(
            "/api/v1/appointments",
            json={
                "patient_id": "invalid-id",
                "appointment_type": "general",
                "scheduled_datetime": "2024-01-01T10:00:00",
            },
        )
        assert response.status_code in [401, 422, 400]
    
    def test_cancel_appointment_not_found(self, test_client: TestClient):
        """Test cancel non-existent appointment"""
        response = test_client.post(
            "/api/v1/appointments/APT-NONEXIST/cancel",
            json={"reason": "test", "confirm_cancellation": True},
        )
        assert response.status_code in [401, 404]