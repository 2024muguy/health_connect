"""
HealthConnect AI - Compliance Agent
====================================
Ensures policy and regulatory compliance.

Features:
- Knowledge Base scope checking
- Privacy compliance
- Regulatory compliance
- Audit trail generation
"""

import re
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
from config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class ComplianceAgent(BaseAgent):
    """
    Compliance Agent.
    Ensures all responses comply with policies and regulations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.COMPLIANCE, config)
        
        # Privacy-related terms
        self.privacy_terms = [
            'hipaa', 'privacy', 'confidential', 'protected health',
            'personal health', 'medical record', 'patient data',
        ]
        
        # Regulatory requirements
        self.regulatory_requirements = {
            "hipaa": "Health Insurance Portability and Accountability Act",
            "gdpr": "General Data Protection Regulation",
        }
        
        logger.info("ComplianceAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute compliance check.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Compliance result
        """
        start_time = time.time()
        
        violations = []
        
        # Check for privacy violations
        privacy_violations = self._check_privacy(context)
        if privacy_violations:
            violations.extend(privacy_violations)
        
        # Check for scope violations
        scope_violations = self._check_scope(context)
        if scope_violations:
            violations.extend(scope_violations)
        
        # Check for regulatory violations
        regulatory_violations = self._check_regulatory(context)
        if regulatory_violations:
            violations.extend(regulatory_violations)
        
        is_compliant = len(violations) == 0
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED if is_compliant else AgentStatus.BLOCKED,
            output={
                "is_compliant": is_compliant,
                "violations": violations,
                "compliance_score": 1.0 if is_compliant else 0.5,
            },
            confidence=0.9,
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    
    def _check_privacy(self, context: AgentContext) -> List[Dict[str, str]]:
        """Check for privacy violations"""
        violations = []
        
        query_lower = context.query.lower()
        
        for term in self.privacy_terms:
            if term in query_lower:
                violations.append({
                    "type": "privacy_concern",
                    "term": term,
                    "severity": "high",
                    "message": f"Query contains privacy-related term: {term}",
                })
        
        return violations
    
    def _check_scope(self, context: AgentContext) -> List[Dict[str, str]]:
        """Check for scope violations"""
        violations = []
        
        # Check if query is asking for information outside knowledge base
        out_of_scope_patterns = [
            r'what.*(?:other|different) clinic',
            r'compare.*(?:clinic|hospital)',
            r'what.*(?:competitor|other provider)',
        ]
        
        query_lower = context.query.lower()
        
        for pattern in out_of_scope_patterns:
            if re.search(pattern, query_lower):
                violations.append({
                    "type": "scope_violation",
                    "pattern": pattern,
                    "severity": "medium",
                    "message": "Query asks for information outside approved scope",
                })
        
        return violations
    
    def _check_regulatory(self, context: AgentContext) -> List[Dict[str, str]]:
        """Check for regulatory violations"""
        violations = []
        
        # Check for requests that would violate regulations
        regulatory_patterns = [
            r'share.*(?:medical|health).*information',
            r'disclose.*(?:patient|medical)',
            r'access.*(?:someone else|another patient)',
        ]
        
        query_lower = context.query.lower()
        
        for pattern in regulatory_patterns:
            if re.search(pattern, query_lower):
                violations.append({
                    "type": "regulatory_violation",
                    "pattern": pattern,
                    "severity": "critical",
                    "message": "Query may violate healthcare regulations",
                })
        
        return violations
    
    def generate_audit_trail(
        self,
        context: AgentContext,
        result: AgentResult,
    ) -> Dict[str, Any]:
        """
        Generate audit trail for compliance.
        
        Args:
            context: Agent context
            result: Agent result
            
        Returns:
            Dict: Audit trail entry
        """
        return {
            "timestamp": time.time(),
            "conversation_id": context.conversation_id,
            "query": context.query,
            "compliance_status": "compliant" if result.is_successful else "non_compliant",
            "violations": result.output.get("violations", []),
            "agent_id": self.agent_id,
        }