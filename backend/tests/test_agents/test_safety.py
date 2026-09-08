"""
HealthConnect AI - Safety Agent Tests
======================================
Tests for SafetyAgent.
"""

import pytest

from app.agents.safety_agents.safety_agent import SafetyAgent
from app.agents.base_agent import AgentContext, AgentStatus


class TestSafetyAgent:
    """Test safety agent"""
    
    @pytest.fixture
    def agent(self):
        """Create safety agent"""
        return SafetyAgent()
    
    @pytest.fixture
    def context(self):
        """Create test context"""
        return AgentContext(
            conversation_id="test-conv",
            query="",
        )
    
    @pytest.mark.asyncio
    async def test_safe_query(self, agent, context):
        """Test safe query"""
        context.query = "How do I book an appointment?"
        result = await agent.run(context)
        
        assert result.status == AgentStatus.COMPLETED
        assert result.output["safety_category"] == "safe"
        assert result.output["action"] == "allow"
    
    @pytest.mark.asyncio
    async def test_emergency_query(self, agent, context):
        """Test emergency detection"""
        context.query = "I'm having chest pain!"
        result = await agent.run(context)
        
        assert result.status == AgentStatus.BLOCKED
        assert result.output["safety_category"] == "emergency"
        assert result.output["action"] == "emergency_protocol"
    
    @pytest.mark.asyncio
    async def test_medical_advice_query(self, agent, context):
        """Test medical advice detection"""
        context.query = "What should I take for my headache?"
        result = await agent.run(context)
        
        assert result.status == AgentStatus.BLOCKED
        assert result.output["safety_category"] == "medical_advice_request"