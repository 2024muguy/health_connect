"""
HealthConnect AI - Test Configuration
======================================
Pytest fixtures and configuration.

Fixtures:
- event_loop
- test_settings
- test_client
- sample_data
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator, Dict, Any
from pathlib import Path

from fastapi.testclient import TestClient

from config.settings import Settings, get_settings
from config.logging_config import setup_logging


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Get test settings"""
    setup_logging(log_level="DEBUG", environment="test")
    return get_settings()


@pytest.fixture(scope="session")
def test_client():
    """Create test client"""
    from app.main import create_app
    
    app = create_app()
    client = TestClient(app)
    return client


@pytest.fixture
def sample_patient_data() -> Dict[str, Any]:
    """Sample patient data for tests"""
    return {
        "patient_code": "PAT-TEST0001",
        "first_name": "Test",
        "last_name": "Patient",
        "email": "test.patient@example.com",
        "phone_number": "+1-555-123-4567",
    }


@pytest.fixture
def sample_appointment_data() -> Dict[str, Any]:
    """Sample appointment data for tests"""
    from datetime import datetime, timedelta, timezone
    
    return {
        "appointment_code": "APT-TEST0001",
        "patient_id": "PAT-TEST0001",
        "appointment_type": "general",
        "scheduled_datetime": datetime.now(timezone.utc) + timedelta(days=1),
        "duration_minutes": 30,
    }


@pytest.fixture
def sample_conversation_data() -> Dict[str, Any]:
    """Sample conversation data for tests"""
    return {
        "conversation_code": "CONV-TEST0001",
        "session_token": "test-session-token",
        "status": "active",
    }


@pytest.fixture
def sample_queries() -> list:
    """Sample test queries"""
    return [
        {
            "query": "Where is HealthConnect Clinic located?",
            "expected_intent": "clinic_information",
            "expected_safety": "safe",
        },
        {
            "query": "How do I book an appointment?",
            "expected_intent": "appointment_booking",
            "expected_safety": "safe",
        },
        {
            "query": "I have a headache, what should I take?",
            "expected_intent": "medical_advice_request",
            "expected_safety": "medical_advice_request",
        },
        {
            "query": "I'm having chest pain!",
            "expected_intent": "emergency",
            "expected_safety": "emergency",
        },
    ]