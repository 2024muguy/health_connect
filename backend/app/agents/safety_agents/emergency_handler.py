"""
HealthConnect AI - Emergency Handler
=====================================
Handles medical emergency situations.

Features:
- Emergency detection
- Emergency response generation
- Emergency escalation
- Emergency logging
"""

import time
from typing import List, Dict, Any, Optional

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)

from config.logging_config import get_logger

logger = get_logger(__name__)


class EmergencyHandler(BaseAgent):
    """
    Emergency Handler Agent.
    Manages medical emergency situations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.EMERGENCY, config)
        
        # Emergency response templates
        self.emergency_responses = {
            "general": (
                "IMPORTANT: If you are experiencing a medical emergency, "
                "please call 911 (or your local emergency number) immediately.\n\n"
                "Do not wait for a response from this assistant.\n\n"
                "If possible, have someone stay with you until help arrives."
            ),
            "chest_pain": (
                "IMPORTANT: Chest pain can be a sign of a heart attack.\n\n"
                "1. Call 911 immediately\n"
                "2. Stop all activity and rest\n"
                "3. If you have been prescribed nitroglycerin, take it as directed\n"
                "4. Do not drive yourself to the hospital\n\n"
                "Emergency services will provide further instructions."
            ),
            "breathing": (
                "IMPORTANT: Difficulty breathing is a medical emergency.\n\n"
                "1. Call 911 immediately\n"
                "2. Sit upright and try to stay calm\n"
                "3. Loosen any tight clothing\n"
                "4. If you have an inhaler, use it as prescribed\n\n"
                "Do not lie down. Emergency services will provide further instructions."
            ),
            "bleeding": (
                "IMPORTANT: Severe bleeding is a medical emergency.\n\n"
                "1. Call 911 immediately\n"
                "2. Apply direct pressure to the wound with a clean cloth\n"
                "3. Do not remove the cloth if it becomes soaked\n"
                "4. Elevate the injured area if possible\n\n"
                "Continue applying pressure until help arrives."
            ),
            "stroke": (
                "IMPORTANT: Stroke symptoms require immediate medical attention.\n\n"
                "1. Call 911 immediately\n"
                "2. Note the time when symptoms first appeared\n"
                "3. Stay calm and lie down\n"
                "4. Do not eat or drink anything\n\n"
                "Time is critical for stroke treatment."
            ),
        }
        
        # Emergency categories
        self.emergency_categories = {
            "chest_pain": ["chest pain", "heart attack", "chest tightness"],
            "breathing": ["difficulty breathing", "can't breathe", "short of breath", "suffocating"],
            "bleeding": ["severe bleeding", "bleeding heavily", "won't stop bleeding"],
            "stroke": ["stroke", "face drooping", "arm weakness", "speech difficulty", "numbness"],
            "unconscious": ["unconscious", "passed out", "not responsive", "collapsed"],
        }
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Handle emergency situation.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Emergency response
        """
        start_time = time.time()
        query = context.query.lower()
        
        # Determine emergency type
        emergency_type = self._determine_emergency_type(query)
        
        # Generate emergency response
        response_text = self._generate_emergency_response(emergency_type)
        
        # Log emergency
        self._log_emergency(context, emergency_type)
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.BLOCKED,
            output={
                "response": response_text,
                "emergency_type": emergency_type,
                "action": "emergency_protocol",
                "requires_human": True,
                "emergency_contact": "911",
            },
            confidence=1.0,
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={
                "emergency": True,
                "emergency_type": emergency_type,
                "logged": True,
            },
        )
    
    def _determine_emergency_type(self, query: str) -> str:
        """
        Determine emergency type from query.
        
        Args:
            query: Query text
            
        Returns:
            str: Emergency type
        """
        for emergency_type, keywords in self.emergency_categories.items():
            if any(keyword in query for keyword in keywords):
                return emergency_type
        
        return "general"
    
    def _generate_emergency_response(self, emergency_type: str) -> str:
        """
        Generate emergency response.
        
        Args:
            emergency_type: Type of emergency
            
        Returns:
            str: Emergency response text
        """
        return self.emergency_responses.get(
            emergency_type,
            self.emergency_responses["general"],
        )
    
    def _log_emergency(self, context: AgentContext, emergency_type: str) -> None:
        """
        Log emergency for audit.
        
        Args:
            context: Agent context
            emergency_type: Emergency type
        """
        logger.critical(
            f"EMERGENCY DETECTED: Type={emergency_type}, "
            f"Conversation={context.conversation_id}, "
            f"Query='{context.query[:100]}'"
        )