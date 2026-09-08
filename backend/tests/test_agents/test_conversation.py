"""
HealthConnect AI - Conversation Agent Tests
============================================
Tests for ConversationAgent.
"""

import pytest

from app.agents.core_agents.conversation_agent import ConversationAgent
from app.agents.base_agent import AgentContext, AgentStatus


class TestConversationAgent:
    """Test conversation agent"""
    
    @pytest.fixture
    def agent(self):
        """Create conversation agent"""
        return ConversationAgent()
    
    @pytest.fixture
    def context(self):
        """Create test context"""
        return AgentContext(
            conversation_id="test-conv",
            query="Test query",
            retrieved_chunks=[
                {
                    "chunk_id": "chunk_1",
                    "text": "HealthConnect Clinic is located at 123 Main Street.",
                    "score": 0.9,
                }
            ],
        )
    
    @pytest.mark.asyncio
    async def test_generate_response_without_llm(self, agent, context):
        """Test response generation without LLM"""
        result = await agent.run(context)
        
        assert result.status == AgentStatus.COMPLETED
        assert "response" in result.output
        assert len(result.output["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_response_no_context(self, agent, context):
        """Test response with no context"""
        context.retrieved_chunks = []
        result = await agent.run(context)
        
        assert result.status == AgentStatus.COMPLETED
        assert "response" in result.output