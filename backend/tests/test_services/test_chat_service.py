"""
HealthConnect AI - Chat Service Tests
======================================
Tests for ChatService.
"""

import pytest

from app.services.chat_service import ChatService


class TestChatService:
    """Test chat service"""
    
    @pytest.fixture
    def service(self):
        """Create chat service"""
        return ChatService()
    
    @pytest.mark.asyncio
    async def test_process_message(self, service):
        """Test message processing"""
        response = await service.process_message(
            message="How do I book an appointment?",
            session_token="test-token",
        )
        
        assert response is not None
        assert "conversation_id" in response
        assert "message" in response
    
    @pytest.mark.asyncio
    async def test_conversation_history(self, service):
        """Test conversation history tracking"""
        await service.process_message("First message", session_token="test-1")
        await service.process_message("Second message", conversation_id="test-1")
        
        history = await service.get_conversation_history("test-1")
        assert len(history) >= 2
    
    @pytest.mark.asyncio
    async def test_end_conversation(self, service):
        """Test ending conversation"""
        await service.process_message("Test message", session_token="test-end")
        result = await service.end_conversation("test-end")
        
        assert result["status"] in ["ended", "not_found"]