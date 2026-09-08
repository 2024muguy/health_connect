"""
HealthConnect AI - Intent Router Tests
=======================================
Tests for IntentRouterAgent.
"""

import pytest

from app.agents.core_agents.intent_router import IntentRouterAgent
from app.agents.base_agent import AgentContext, AgentStatus


class TestIntentRouterAgent:
    """Test intent router agent"""
    
    @pytest.fixture
    def agent(self):
        """Create intent router agent"""
        return IntentRouterAgent()
    
    @pytest.fixture
    def context(self):
        """Create test context"""
        return AgentContext(
            conversation_id="test-conv",
            query="",
        )
    
    @pytest.mark.asyncio
    async def test_classify_appointment_booking(self, agent, context):
        """Test appointment booking classification"""
        context.query = "How do I book an appointment?"
        result = await agent.run(context)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.output["intent"] == "appointment_booking"
    
    @pytest.mark.asyncio
    async def test_classify_emergency(self, agent, context):
        """Test emergency classification"""
        context.query = "I'm having chest pain!"
        result = await agent.run(context)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.output["intent"] == "emergency"
    
    @pytest.mark.asyncio
    async def test_classify_medical_advice(self, agent, context):
        """Test medical advice classification"""
        context.query = "What medication should I take for a cold?"
        result = await agent.run(context)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.output["intent"] == "medical_advice_request"