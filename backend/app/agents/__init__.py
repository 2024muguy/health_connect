"""
HealthConnect AI - Agents Package
==================================
Multi-agent orchestration system.

Agents:
- Intent Router Agent
- Conversation Agent
- Knowledge Agent
- Action Agent
- Safety Agent
- Compliance Agent
- Emergency Handler
- Summary Agent
- Feedback Agent
- Analytics Agent

This package provides:
- Base agent classes
- Orchestrator for agent coordination
- Message bus for inter-agent communication
"""

from app.agents.base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus
from app.agents.orchestrator import Orchestrator
from app.agents.message_bus import MessageBus, AgentMessage, MessageType

__all__ = [
    "BaseAgent",
    "AgentContext",
    "AgentResult",
    "AgentStatus",
    "Orchestrator",
    "MessageBus",
    "AgentMessage",
    "MessageType",
]