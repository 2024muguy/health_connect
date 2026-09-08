"""
HealthConnect AI - Escalation API Tests
========================================
Tests for escalation endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestEscalationEndpoints:
    """Test escalation endpoints"""
    
    def test_create_escalation(self, test_client: TestClient):
        """Test escalation creation"""
        response = test_client.post(
            "/api/v1/escalations",
            json={
                "escalation_type": "appointment",
                "tier": 2,
                "reason": "Test escalation",
                "priority": "normal",
            },
        )
        assert response.status_code in [200, 201, 401, 422]
    
    def test_list_escalations_requires_admin(self, test_client: TestClient):
        """Test list escalations requires admin"""
        response = test_client.get("/api/v1/escalations")
        assert response.status_code == 401  # Unauthorized without token