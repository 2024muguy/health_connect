"""
HealthConnect AI - Summary Agent
=================================
Summarizes conversations and extracts key information.

Features:
- Conversation summarization
- Key point extraction
- Action item tracking
- Topic identification
"""

import time
from typing import List, Dict, Any, Optional
from collections import Counter

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)

from config.logging_config import get_logger

logger = get_logger(__name__)


class SummaryAgent(BaseAgent):
    """
    Summary Agent.
    Generates conversation summaries and extracts key information.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.SUMMARY, config)
        logger.info("SummaryAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Generate conversation summary.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Summary result
        """
        start_time = time.time()
        
        # Generate summary
        summary = self._generate_summary(context)
        
        # Extract key points
        key_points = self._extract_key_points(context)
        
        # Identify topics
        topics = self._identify_topics(context)
        
        # Extract action items
        action_items = self._extract_action_items(context)
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "summary": summary,
                "key_points": key_points,
                "topics": topics,
                "action_items": action_items,
            },
            confidence=0.85,
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    
    def _generate_summary(self, context: AgentContext) -> str:
        """
        Generate conversation summary.
        
        Args:
            context: Agent context
            
        Returns:
            str: Summary text
        """
        if self.llm_provider:
            return self._llm_summary(context)
        
        return self._rule_based_summary(context)
    
    def _llm_summary(self, context: AgentContext) -> str:
        """Generate summary using LLM"""
        from app.llm.base import LLMMessage
        from config.prompts.prompt_templates import SummaryPromptTemplate
        
        # Build conversation text
        conversation_text = f"User Query: {context.query}\n"
        for msg in context.history[-10:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            conversation_text += f"{role.upper()}: {content}\n"
        
        prompt = SummaryPromptTemplate.CONVERSATION_SUMMARY.format(
            conversation=conversation_text,
        )
        
        messages = [
            LLMMessage(role="system", content="You are a conversation summarizer."),
            LLMMessage(role="user", content=prompt),
        ]
        
        # Note: This would need to be async in production
        # For now, return a basic summary
        return self._rule_based_summary(context)
    
    def _rule_based_summary(self, context: AgentContext) -> str:
        """Generate rule-based summary"""
        parts = []
        
        if context.intent:
            parts.append(f"User intent: {context.intent}")
        
        parts.append(f"User query: {context.query[:100]}")
        
        if context.retrieved_chunks:
            parts.append(f"Information retrieved from {len(context.retrieved_chunks)} sources")
        
        if context.safety_flags:
            parts.append(f"Safety flags: {', '.join(context.safety_flags.keys())}")
        
        return " | ".join(parts)
    
    def _extract_key_points(self, context: AgentContext) -> List[str]:
        """Extract key points from conversation"""
        key_points = []
        
        if context.intent:
            key_points.append(f"Intent: {context.intent}")
        
        if context.retrieved_chunks:
            key_points.append(f"Retrieved {len(context.retrieved_chunks)} knowledge chunks")
        
        for msg in context.history:
            content = msg.get("content", "")
            if len(content) > 20:
                key_points.append(content[:100])
        
        return key_points[:5]
    
    def _identify_topics(self, context: AgentContext) -> List[str]:
        """Identify conversation topics"""
        # Simple keyword-based topic identification
        topic_keywords = {
            "appointment": ["appointment", "booking", "schedule", "reschedule", "cancel"],
            "billing": ["bill", "payment", "cost", "fee", "insurance", "copay"],
            "clinic": ["location", "address", "hours", "clinic", "contact"],
            "preparation": ["bring", "prepare", "before", "expect"],
            "policy": ["policy", "rule", "late", "no-show", "referral"],
            "feedback": ["feedback", "complaint", "review", "satisfied"],
        }
        
        all_text = context.query.lower()
        for msg in context.history:
            all_text += " " + msg.get("content", "").lower()
        
        topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ["general"]
    
    def _extract_action_items(self, context: AgentContext) -> List[Dict[str, str]]:
        """Extract action items from conversation"""
        action_items = []
        
        # Check for appointment actions
        intent = context.intent or ""
        
        action_map = {
            "appointment_booking": {"action": "Book appointment", "status": "pending"},
            "appointment_reschedule": {"action": "Reschedule appointment", "status": "pending_approval"},
            "appointment_cancel": {"action": "Cancel appointment", "status": "pending_approval"},
            "escalation_request": {"action": "Escalate to human", "status": "escalated"},
            "feedback": {"action": "Log feedback", "status": "completed"},
        }
        
        if intent in action_map:
            action_items.append(action_map[intent])
        
        return action_items