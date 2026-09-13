"""
HealthConnect AI - Agent Setup
================================
Registers all agents with the orchestrator.
"""

from typing import List

from app.agents.base_agent import BaseAgent, AgentType
from app.agents.orchestrator import Orchestrator
from app.agents.core_agents.intent_router import IntentRouterAgent
from app.agents.core_agents.conversation_agent import ConversationAgent
from app.agents.core_agents.action_agent import ActionAgent
from app.agents.core_agents.knowledge_agent import KnowledgeAgent
from app.agents.safety_agents.safety_agent import SafetyAgent

from config.logging_config import get_logger

logger = get_logger(__name__)


def setup_agents(orchestrator: Orchestrator) -> None:
    """Register all agents with the orchestrator."""
    
    agents: List[BaseAgent] = [
        IntentRouterAgent(),
        SafetyAgent(),
        KnowledgeAgent(),
        ConversationAgent(),
        ActionAgent(),
    ]
    
    orchestrator.register_agents(agents)
    
    logger.info(f"Registered {len(agents)} agents:")
    for agent in agents:
        logger.info(f"  - {agent.agent_type.value}")
