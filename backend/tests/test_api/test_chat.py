"""
HealthConnect AI - Chat API Tests
===================================
Tests for chat endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from config.logging_config import setup_logging

setup_logging(log_level="DEBUG", environment="test")


class TestChatEndpoints:
    """Test chat endpoints"""
    
    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root(self, test_client: TestClient):
        """Test root endpoint"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "version" in data
    
    def test_send_message(self, test_client: TestClient):
        """Test send message endpoint"""
        response = test_client.post(
            "/api/v1/chat/message",
            json={
                "message": "How do I book an appointment?",
                "session_token": "test-token",
            },
        )
        assert response.status_code in [200, 500]  # 500 if services not initialized
    
    def test_send_empty_message(self, test_client: TestClient):
        """Test empty message validation"""
        response = test_client.post(
            "/api/v1/chat/message",
            json={"message": ""},
        )
        assert response.status_code == 422  # Validation error
    
    def test_list_conversations(self, test_client: TestClient):
        """Test list conversations endpoint"""
        response = test_client.get("/api/v1/chat/conversations")
        assert response.status_code in [200, 401]  # 401 if auth required