"""
HealthConnect AI - Escalation Service
======================================
Business logic for escalation management.

Features:
- Escalation creation
- Escalation routing
- Escalation tracking
- Escalation resolution
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.models.escalation import (
    Escalation,
    EscalationStatus,
    EscalationTier,
    EscalationType,
)

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EscalationService:
    """
    Escalation Service.
    Manages escalation operations.
    """
    
    def __init__(self):
        self._escalations: Dict[str, Dict[str, Any]] = {}
        logger.info("EscalationService initialized")
    
    async def create_escalation(
        self,
        conversation_id: Optional[str],
        escalation_type: str,
        tier: int,
        reason: str,
        priority: str = "normal",
        department: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new escalation.
        
        Args:
            conversation_id: Related conversation
            escalation_type: Type of escalation
            tier: Escalation tier
            reason: Escalation reason
            priority: Priority level
            department: Target department
            description: Detailed description
            
        Returns:
            Dict: Created escalation
        """
        escalation_code = f"ESC-{uuid.uuid4().hex[:8].upper()}"
        
        escalation = {
            "escalation_code": escalation_code,
            "conversation_id": conversation_id,
            "escalation_type": escalation_type,
            "tier": tier,
            "status": EscalationStatus.PENDING.value,
            "priority": priority,
            "department": department or self._determine_department(escalation_type),
            "reason": reason,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "assigned_to": None,
            "resolved_at": None,
            "resolution": None,
        }
        
        self._escalations[escalation_code] = escalation
        logger.info(f"Created escalation: {escalation_code}")
        
        return escalation
    
    def _determine_department(self, escalation_type: str) -> str:
        """Determine department for escalation type"""
        department_map = {
            "appointment": "scheduling",
            "billing": "billing",
            "insurance": "billing",
            "clinical": "clinical",
            "safety": "safety",
            "emergency": "emergency",
            "technical": "it_support",
            "complaint": "administration",
            "feedback": "administration",
        }
        return department_map.get(escalation_type, "administration")
    
    async def assign_escalation(
        self,
        escalation_code: str,
        staff_member: str,
    ) -> Dict[str, Any]:
        """
        Assign escalation to staff member.
        
        Args:
            escalation_code: Escalation code
            staff_member: Staff member name
            
        Returns:
            Dict: Updated escalation
        """
        escalation = self._escalations.get(escalation_code)
        
        if not escalation:
            return {"status": "not_found", "escalation_code": escalation_code}
        
        escalation["status"] = EscalationStatus.ASSIGNED.value
        escalation["assigned_to"] = staff_member
        escalation["assigned_at"] = datetime.now(timezone.utc).isoformat()
        
        return escalation
    
    async def resolve_escalation(
        self,
        escalation_code: str,
        resolution: str,
        resolved_by: str,
    ) -> Dict[str, Any]:
        """
        Resolve an escalation.
        
        Args:
            escalation_code: Escalation code
            resolution: Resolution details
            resolved_by: Staff member who resolved
            
        Returns:
            Dict: Updated escalation
        """
        escalation = self._escalations.get(escalation_code)
        
        if not escalation:
            return {"status": "not_found", "escalation_code": escalation_code}
        
        escalation["status"] = EscalationStatus.RESOLVED.value
        escalation["resolution"] = resolution
        escalation["resolved_by"] = resolved_by
        escalation["resolved_at"] = datetime.now(timezone.utc).isoformat()
        
        return escalation
    
    async def get_escalation(self, escalation_code: str) -> Optional[Dict[str, Any]]:
        """Get escalation by code"""
        return self._escalations.get(escalation_code)
    
    async def list_escalations(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        department: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List escalations with filters.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            department: Filter by department
            limit: Maximum results
            
        Returns:
            List[Dict]: Escalations
        """
        escalations = list(self._escalations.values())
        
        if status:
            escalations = [e for e in escalations if e["status"] == status]
        
        if priority:
            escalations = [e for e in escalations if e["priority"] == priority]
        
        if department:
            escalations = [e for e in escalations if e["department"] == department]
        
        return escalations[:limit]
    
    async def process_pending_escalations(self) -> int:
        """
        Process pending escalations.
        
        Returns:
            int: Number of escalations processed
        """
        pending = [
            e for e in self._escalations.values()
            if e["status"] == EscalationStatus.PENDING.value
        ]
        
        # In production, this would notify staff
        for escalation in pending:
            logger.info(f"Processing pending escalation: {escalation['escalation_code']}")
        
        return len(pending)
    
    async def get_pending_count(self) -> int:
        """Get count of pending escalations"""
        return sum(
            1 for e in self._escalations.values()
            if e["status"] == EscalationStatus.PENDING.value
        )
    
    async def get_critical_count(self) -> int:
        """Get count of critical escalations"""
        return sum(
            1 for e in self._escalations.values()
            if e["priority"] == "critical"
            and e["status"] != EscalationStatus.RESOLVED.value
        )