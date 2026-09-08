"""
HealthConnect AI - Action Agent
================================
Executes administrative actions.

Features:
- Appointment management
- Task creation
- Human approval workflow
- Notification triggering
"""

import time
from typing import List, Dict, Any, Optional
from enum import Enum

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)

from config.logging_config import get_logger

logger = get_logger(__name__)


class ActionType(Enum):
    """Action type enumeration"""
    BOOK_APPOINTMENT = "book_appointment"
    RESCHEDULE_APPOINTMENT = "reschedule_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    SEND_REMINDER = "send_reminder"
    CREATE_ESCALATION = "create_escalation"
    LOG_FEEDBACK = "log_feedback"
    NONE = "none"


class ActionAgent(BaseAgent):
    """
    Action Agent.
    Executes administrative actions based on intent.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.ACTION, config)
        
        # Actions requiring human approval
        self.approval_required_actions = {
            ActionType.CANCEL_APPOINTMENT,
            ActionType.RESCHEDULE_APPOINTMENT,
        }
        
        logger.info("ActionAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute action based on intent.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Action result
        """
        start_time = time.time()
        
        # Determine action from intent
        action = self._determine_action(context)
        
        if action == ActionType.NONE:
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={"action": "none", "result": None},
                confidence=0.0,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Check if action requires approval
        requires_approval = action in self.approval_required_actions
        
        # Execute action
        try:
            result = await self._execute_action(action, context)
            
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={
                    "action": action.value,
                    "result": result,
                    "requires_human": requires_approval,
                    "status": "pending_approval" if requires_approval else "completed",
                },
                confidence=0.9,
                execution_time_ms=(time.time() - start_time) * 1000,
                metadata={
                    "requires_approval": requires_approval,
                    "action_type": action.value,
                },
            )
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
    
    def _determine_action(self, context: AgentContext) -> ActionType:
        """
        Determine action from intent.
        
        Args:
            context: Agent context
            
        Returns:
            ActionType: Action to execute
        """
        intent = context.intent or ""
        
        intent_to_action = {
            "appointment_booking": ActionType.BOOK_APPOINTMENT,
            "appointment_reschedule": ActionType.RESCHEDULE_APPOINTMENT,
            "appointment_cancel": ActionType.CANCEL_APPOINTMENT,
            "feedback": ActionType.LOG_FEEDBACK,
            "escalation_request": ActionType.CREATE_ESCALATION,
        }
        
        return intent_to_action.get(intent, ActionType.NONE)
    
    async def _execute_action(
        self,
        action: ActionType,
        context: AgentContext,
    ) -> Dict[str, Any]:
        """
        Execute specific action.
        
        Args:
            action: Action to execute
            context: Agent context
            
        Returns:
            Dict: Action result
        """
        if action == ActionType.BOOK_APPOINTMENT:
            return await self._book_appointment(context)
        elif action == ActionType.RESCHEDULE_APPOINTMENT:
            return await self._reschedule_appointment(context)
        elif action == ActionType.CANCEL_APPOINTMENT:
            return await self._cancel_appointment(context)
        elif action == ActionType.SEND_REMINDER:
            return await self._send_reminder(context)
        elif action == ActionType.CREATE_ESCALATION:
            return await self._create_escalation(context)
        elif action == ActionType.LOG_FEEDBACK:
            return await self._log_feedback(context)
        else:
            return {"status": "not_implemented"}
    
    async def _book_appointment(self, context: AgentContext) -> Dict[str, Any]:
        """Book appointment action"""
        return {
            "status": "info_provided",
            "message": "Appointment booking information provided to user",
            "next_steps": [
                "User needs to call clinic or use online portal",
                "Required information: name, insurance, preferred time",
            ],
        }
    
    async def _reschedule_appointment(self, context: AgentContext) -> Dict[str, Any]:
        """Reschedule appointment action"""
        return {
            "status": "pending_approval",
            "message": "Rescheduling request created",
            "requires_staff_approval": True,
            "approval_time_estimate": "2 business hours",
        }
    
    async def _cancel_appointment(self, context: AgentContext) -> Dict[str, Any]:
        """Cancel appointment action"""
        return {
            "status": "pending_approval",
            "message": "Cancellation request created",
            "requires_staff_approval": True,
            "approval_time_estimate": "2 business hours",
        }
    
    async def _send_reminder(self, context: AgentContext) -> Dict[str, Any]:
        """Send reminder action"""
        return {
            "status": "scheduled",
            "message": "Appointment reminder scheduled",
            "reminder_time": "24 hours before appointment",
        }
    
    async def _create_escalation(self, context: AgentContext) -> Dict[str, Any]:
        """Create escalation action"""
        return {
            "status": "escalated",
            "message": "Escalation ticket created",
            "department": self._determine_department(context),
            "priority": "normal",
        }
    
    async def _log_feedback(self, context: AgentContext) -> Dict[str, Any]:
        """Log feedback action"""
        return {
            "status": "logged",
            "message": "Feedback recorded",
        }
    
    def _determine_department(self, context: AgentContext) -> str:
        """Determine department for escalation"""
        intent = context.intent or ""
        
        department_map = {
            "appointment_booking": "scheduling",
            "appointment_reschedule": "scheduling",
            "appointment_cancel": "scheduling",
            "billing_query": "billing",
            "insurance_query": "billing",
            "medical_advice_request": "clinical",
            "emergency": "emergency",
            "feedback": "administration",
        }
        
        return department_map.get(intent, "administration")