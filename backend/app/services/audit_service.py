"""
HealthConnect AI - Audit Service
=================================
Business logic for audit trail management.

Features:
- Audit event logging
- Audit trail retrieval
- Compliance tracking
- Security event logging
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AuditService:
    """
    Audit Service.
    Manages audit trail for compliance and security.
    """
    
    def __init__(self):
        self._audit_log: List[Dict[str, Any]] = []
        self._max_log_size = 10000
        logger.info("AuditService initialized")
    
    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info",
    ) -> Dict[str, Any]:
        """
        Log an audit event.
        
        Args:
            event_type: Event type
            user_id: User ID
            conversation_id: Conversation ID
            details: Event details
            severity: Event severity
            
        Returns:
            Dict: Logged event
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "details": details or {},
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip_address": details.get("ip_address") if details else None,
        }
        
        self._audit_log.append(event)
        
        # Trim log if needed
        if len(self._audit_log) > self._max_log_size:
            self._audit_log = self._audit_log[-self._max_log_size:]
        
        # Log based on severity
        if severity == "critical":
            logger.critical(f"AUDIT: {event_type} - {details}")
        elif severity == "warning":
            logger.warning(f"AUDIT: {event_type} - {details}")
        else:
            logger.info(f"AUDIT: {event_type}")
        
        return event
    
    async def log_safety_event(
        self,
        conversation_id: str,
        safety_category: str,
        action_taken: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Log a safety event.
        
        Args:
            conversation_id: Conversation ID
            safety_category: Safety category
            action_taken: Action taken
            details: Event details
            
        Returns:
            Dict: Logged event
        """
        return await self.log_event(
            event_type="safety_violation",
            conversation_id=conversation_id,
            details={
                "safety_category": safety_category,
                "action_taken": action_taken,
                **(details or {}),
            },
            severity="warning",
        )
    
    async def log_emergency_event(
        self,
        conversation_id: str,
        emergency_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Log an emergency event.
        
        Args:
            conversation_id: Conversation ID
            emergency_type: Emergency type
            details: Event details
            
        Returns:
            Dict: Logged event
        """
        return await self.log_event(
            event_type="emergency_detected",
            conversation_id=conversation_id,
            details={
                "emergency_type": emergency_type,
                **(details or {}),
            },
            severity="critical",
        )
    
    async def log_appointment_action(
        self,
        action: str,
        appointment_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Log appointment action.
        
        Args:
            action: Action type (book, reschedule, cancel)
            appointment_id: Appointment ID
            user_id: User ID
            details: Event details
            
        Returns:
            Dict: Logged event
        """
        return await self.log_event(
            event_type=f"appointment_{action}",
            user_id=user_id,
            details={
                "appointment_id": appointment_id,
                **(details or {}),
            },
            severity="info",
        )
    
    async def get_audit_trail(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail with filters.
        
        Args:
            event_type: Filter by event type
            severity: Filter by severity
            user_id: Filter by user
            limit: Maximum results
            
        Returns:
            List[Dict]: Audit events
        """
        events = self._audit_log
        
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        if severity:
            events = [e for e in events if e["severity"] == severity]
        
        if user_id:
            events = [e for e in events if e["user_id"] == user_id]
        
        return events[-limit:]
    
    async def get_security_events(
        self,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get security-related events.
        
        Args:
            limit: Maximum results
            
        Returns:
            List[Dict]: Security events
        """
        security_types = [
            "safety_violation",
            "emergency_detected",
            "authentication_failure",
            "authorization_failure",
            "rate_limit_exceeded",
        ]
        
        events = [
            e for e in self._audit_log
            if e["event_type"] in security_types
        ]
        
        return events[-limit:]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics"""
        return {
            "total_events": len(self._audit_log),
            "event_types": list(set(e["event_type"] for e in self._audit_log)),
            "severity_counts": {
                severity: sum(1 for e in self._audit_log if e["severity"] == severity)
                for severity in ["info", "warning", "critical"]
            },
        }
    
    async def clear_log(self) -> None:
        """Clear audit log"""
        self._audit_log = []
        logger.info("Audit log cleared")