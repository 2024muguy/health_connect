"""
HealthConnect AI - Safety Agent
================================
Monitors and enforces safety boundaries.

Features:
- Medical advice detection
- Emergency detection
- PII detection
- Abusive language detection
- Risk scoring
- Safety classification
"""

import re
import time
from typing import List, Dict, Any, Optional, Tuple

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)

from config.logging_config import get_logger
from config.settings import get_settings
from config.constants import SAFETY_CATEGORIES, SAFETY_ACTIONS, SAFETY_SEVERITY
from config.prompts.prompt_templates import SafetyPromptTemplate

logger = get_logger(__name__)
settings = get_settings()


class SafetyAgent(BaseAgent):
    """
    Safety Agent.
    Monitors all interactions for safety violations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.SAFETY, config)
        
        # Safety rules and patterns
        self.emergency_terms = set(settings.safety.emergency_terms)
        self.medical_terms = set(settings.safety.medical_terms)
        
        # PII patterns
        self.pii_patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'),
        }
        
        # Abusive language patterns
        self.abusive_patterns = [
            r'\bstupid\b',
            r'\bidiot\b',
            r'\bdumb\b',
            r'\bhate\b',
            r'\bterrible\b',
            r'\bawful\b',
            r'\bworthless\b',
            r'\buseless\b',
        ]
        
        logger.info("SafetyAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute safety check on query.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Safety check result
        """
        start_time = time.time()
        query = context.query.lower().strip()
        
        # Check for emergency
        if self._check_emergency(query):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.BLOCKED,
                output={
                    "safety_category": "emergency",
                    "action": "emergency_protocol",
                    "safety_score": 0.0,
                    "risk_score": 100,
                    "violations": ["emergency_detected"],
                    "message": "Medical emergency detected",
                },
                confidence=1.0,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Check for medical advice request
        if self._check_medical_advice(query):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.BLOCKED,
                output={
                    "safety_category": "medical_advice_request",
                    "action": "block",
                    "safety_score": 0.2,
                    "risk_score": 80,
                    "violations": ["medical_advice_request"],
                    "message": "Medical advice request detected",
                },
                confidence=0.9,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Check for PII request
        if self._check_pii_request(query):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.BLOCKED,
                output={
                    "safety_category": "pii_request",
                    "action": "block",
                    "safety_score": 0.3,
                    "risk_score": 70,
                    "violations": ["pii_request"],
                    "message": "Personal information request detected",
                },
                confidence=0.9,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Check for prescription request
        if self._check_prescription_request(query):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={
                    "safety_category": "prescription_request",
                    "action": "escalate",
                    "safety_score": 0.4,
                    "risk_score": 60,
                    "violations": ["prescription_request"],
                    "message": "Prescription request detected",
                },
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Check for test result query
        if self._check_test_result_query(query):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={
                    "safety_category": "test_result_query",
                    "action": "escalate",
                    "safety_score": 0.4,
                    "risk_score": 60,
                    "violations": ["test_result_query"],
                    "message": "Test result query detected",
                },
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Check for abusive language
        if self._check_abusive_language(query):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.BLOCKED,
                output={
                    "safety_category": "abusive_language",
                    "action": "block",
                    "safety_score": 0.5,
                    "risk_score": 50,
                    "violations": ["abusive_language"],
                    "message": "Abusive language detected",
                },
                confidence=0.9,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Check for out of scope
        if self._check_out_of_scope(query):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={
                    "safety_category": "out_of_scope",
                    "action": "redirect",
                    "safety_score": 0.7,
                    "risk_score": 10,
                    "violations": ["out_of_scope"],
                    "message": "Query is out of scope",
                },
                confidence=0.7,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Safe query
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "safety_category": "safe",
                "action": "allow",
                "safety_score": 1.0,
                "risk_score": 0,
                "violations": [],
                "message": "Query is safe",
            },
            confidence=1.0,
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    
    def _check_emergency(self, query: str) -> bool:
        """Check for emergency terms"""
        return any(term in query for term in self.emergency_terms)
    
    def _check_medical_advice(self, query: str) -> bool:
        """Check for medical advice request"""
        # Check for medical terms
        has_medical_term = any(term in query for term in self.medical_terms)
        
        # Check for advice-seeking patterns
        advice_patterns = [
            r'what should i (?:take|do|use)',
            r'is (?:this|my|it) (?:serious|normal|bad)',
            r'should i (?:be worried|see a doctor|go to)',
            r'do i (?:need|have) (?:medication|treatment|surgery)',
            r'can you (?:diagnose|treat|prescribe)',
            r'how do i (?:treat|cure|fix)',
        ]
        
        has_advice_pattern = any(re.search(p, query, re.IGNORECASE) for p in advice_patterns)
        
        return has_medical_term and has_advice_pattern
    
    def _check_pii_request(self, query: str) -> bool:
        """Check for PII request"""
        pii_request_patterns = [
            r'social security',
            r'ssn',
            r'password',
            r'credit card',
            r'bank account',
            r'patient.*(?:record|history|information)',
            r'who is.*patient',
            r'what is.*(?:ssn|social)',
        ]
        
        return any(re.search(p, query, re.IGNORECASE) for p in pii_request_patterns)
    
    def _check_prescription_request(self, query: str) -> bool:
        """Check for prescription request"""
        prescription_patterns = [
            r'refill.*(?:prescription|medication|medicine)',
            r'renew.*(?:prescription|medication)',
            r'prescription.*(?:refill|renew)',
            r'can i get.*(?:medication|medicine|prescription)',
            r'increase.*(?:dose|dosage|medication)',
            r'change.*(?:medication|prescription|dose)',
        ]
        
        return any(re.search(p, query, re.IGNORECASE) for p in prescription_patterns)
    
    def _check_test_result_query(self, query: str) -> bool:
        """Check for test result query"""
        test_result_patterns = [
            r'test result',
            r'blood test',
            r'lab result',
            r'x-ray result',
            r'mri result',
            r'ct scan result',
            r'what does my.*(?:test|result|lab)',
            r'interpret.*(?:test|result|lab)',
        ]
        
        return any(re.search(p, query, re.IGNORECASE) for p in test_result_patterns)
    
    def _check_abusive_language(self, query: str) -> bool:
        """Check for abusive language"""
        return any(re.search(p, query, re.IGNORECASE) for p in self.abusive_patterns)
    
    def _check_out_of_scope(self, query: str) -> bool:
        """Check for out of scope query"""
        out_of_scope_terms = [
            'weather', 'sports', 'politics', 'entertainment',
            'movie', 'music', 'game', 'recipe', 'cooking',
        ]
        
        return any(term in query for term in out_of_scope_terms)
    
    async def verify_response(
        self,
        context: AgentContext,
        response_text: str,
    ) -> AgentResult:
        """
        Verify safety of generated response.
        
        Args:
            context: Agent context
            response_text: Generated response
            
        Returns:
            AgentResult: Verification result
        """
        # Check for medical advice in response
        if self._check_medical_advice(response_text):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.BLOCKED,
                output={
                    "safety_category": "medical_advice_in_response",
                    "action": "block",
                    "safety_score": 0.0,
                    "risk_score": 80,
                },
                confidence=0.9,
            )
        
        # Check for hallucination indicators
        if self._check_hallucination_indicators(response_text):
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={
                    "safety_category": "potential_hallucination",
                    "action": "regenerate",
                    "safety_score": 0.5,
                    "risk_score": 40,
                },
                confidence=0.6,
            )
        
        # Response is safe
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "safety_category": "safe",
                "action": "allow",
                "safety_score": 1.0,
                "risk_score": 0,
            },
            confidence=1.0,
        )
    
    def _check_hallucination_indicators(self, response: str) -> bool:
        """Check for hallucination indicators in response"""
        indicators = [
            r'I think',
            r'I believe',
            r'I guess',
            r'probably',
            r'might be',
            r'could be',
            r'not sure',
            r'I am not certain',
        ]
        
        return any(re.search(p, response, re.IGNORECASE) for p in indicators)