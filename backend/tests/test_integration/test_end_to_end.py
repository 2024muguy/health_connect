"""
HealthConnect AI - End-to-End Integration Tests
================================================
Complete system integration tests.
"""

import pytest
from datetime import datetime, timedelta, timezone

from app.services.chat_service import ChatService
from app.services.appointment_service import AppointmentService
from app.services.escalation_service import EscalationService
from app.services.audit_service import AuditService


class TestEndToEnd:
    """End-to-end system tests"""
    
    @pytest.fixture
    def chat_service(self):
        return ChatService()
    
    @pytest.fixture
    def appointment_service(self):
        return AppointmentService()
    
    @pytest.fixture
    def escalation_service(self):
        return EscalationService()
    
    @pytest.fixture
    def audit_service(self):
        return AuditService()
    
    @pytest.mark.asyncio
    async def test_chat_to_appointment_flow(self, chat_service, appointment_service):
        """Test chat -> appointment flow"""
        # User asks about booking
        chat_response = await chat_service.process_message(
            message="I want to book an appointment",
            session_token="e2e-test-1",
        )
        
        assert chat_response is not None
        
        # Create appointment
        appointment = await appointment_service.create_appointment(
            patient_id="PAT-E2E",
            appointment_type="general",
            scheduled_datetime=datetime.now(timezone.utc) + timedelta(days=2),
        )
        
        assert appointment["appointment_code"].startswith("APT-")
    
    @pytest.mark.asyncio
    async def test_escalation_flow(self, chat_service, escalation_service, audit_service):
        """Test escalation flow"""
        # User requests human
        chat_response = await chat_service.process_message(
            message="I want to talk to a human",
            session_token="e2e-test-2",
        )
        
        # Create escalation
        escalation = await escalation_service.create_escalation(
            conversation_id="e2e-test-2",
            escalation_type="appointment",
            tier=2,
            reason="User requested human assistance",
        )
        
        assert escalation["escalation_code"].startswith("ESC-")
        
        # Log audit event
        audit_event = await audit_service.log_event(
            event_type="escalation_created",
            details={"escalation_code": escalation["escalation_code"]},
        )
        
        assert audit_event["event_type"] == "escalation_created"
    
    @pytest.mark.asyncio
    async def test_safety_flow(self, chat_service, audit_service):
        """Test safety flow"""
        # User reports emergency
        chat_response = await chat_service.process_message(
            message="I'm having chest pain!",
            session_token="e2e-test-3",
        )
        
        assert chat_response is not None
        
        # Log emergency
        emergency_event = await audit_service.log_emergency_event(
            conversation_id="e2e-test-3",
            emergency_type="chest_pain",
        )
        
        assert emergency_event["severity"] == "critical"