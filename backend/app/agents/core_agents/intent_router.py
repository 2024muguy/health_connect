"""
HealthConnect AI - Intent Router Agent
=======================================
Classifies user intent for routing to appropriate handlers.

Features:
- Intent classification
- Confidence scoring
- Alternative intent detection
- Routing decision
"""

import re
from typing import List, Dict, Any, Optional, Tuple

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)

from config.logging_config import get_logger
from config.constants import INTENT_LABELS, INTENT_ROUTING_MAP
from config.prompts.prompt_templates import IntentPromptTemplate

logger = get_logger(__name__)


class IntentRouterAgent(BaseAgent):
    """
    Intent Router Agent.
    Classifies user queries into intent categories.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.INTENT_ROUTER, config)
        
        # Intent patterns for rule-based classification (fallback)
        self.intent_patterns = self._build_intent_patterns()
        
        # Intent keywords for quick matching
        self.intent_keywords = self._build_intent_keywords()
        
        logger.info("IntentRouterAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute intent classification.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Classification result
        """
        query = context.query.lower().strip()
        
        # Try LLM-based classification if available
        if self.llm_provider:
            try:
                return await self._llm_classify(context, query)
            except Exception as e:
                logger.warning(f"LLM classification failed: {e}. Using rule-based.")
        
        # Fallback to rule-based classification
        return self._rule_based_classify(query)
    
    async def _llm_classify(
        self,
        context: AgentContext,
        query: str,
    ) -> AgentResult:
        """
        Classify intent using LLM.
        
        Args:
            context: Agent context
            query: Query text
            
        Returns:
            AgentResult: Classification result
        """
        from app.llm.base import LLMMessage
        
        # Build classification prompt
        prompt = IntentPromptTemplate.CLASSIFICATION_PROMPT.format(query=query)
        
        messages = [
            LLMMessage(role="system", content="You are an intent classifier for a healthcare assistant."),
            LLMMessage(role="user", content=prompt),
        ]
        
        # Get LLM response
        response = await self.llm_provider.generate(messages)
        
        # Parse JSON response
        import json
        
        try:
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.text
            
            result = json.loads(json_str)
            
            intent = result.get("intent", "general_faq")
            confidence = float(result.get("confidence", 0.5))
            routing = result.get("routing", INTENT_ROUTING_MAP.get(intent, "knowledge_base"))
            alternatives = result.get("alternative_intents", [])
            
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={
                    "intent": intent,
                    "routing": routing,
                    "alternative_intents": alternatives,
                },
                confidence=confidence,
                metadata={"classification_method": "llm"},
            )
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM classification: {e}")
            return self._rule_based_classify(query)
    
    def _rule_based_classify(self, query: str) -> AgentResult:
        """
        Rule-based intent classification.
        Uses keyword matching and pattern recognition.
        
        Args:
            query: Query text
            
        Returns:
            AgentResult: Classification result
        """
        # Priority order: emergency > medical > specific intents > general
        classification_order = [
            "emergency",
            "medical_advice_request",
            "appointment_cancel",
            "appointment_reschedule",
            "appointment_booking",
            "insurance_query",
            "billing_query",
            "preparation_guidance",
            "policy_query",
            "clinic_information",
            "escalation_request",
            "feedback",
            "general_faq",
        ]
        
        scores = {}
        
        for intent in classification_order:
            keywords = self.intent_keywords.get(intent, [])
            patterns = self.intent_patterns.get(intent, [])
            
            # Keyword matching
            keyword_score = 0
            for keyword in keywords:
                if keyword in query:
                    keyword_score += 1
            
            # Pattern matching
            pattern_score = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    pattern_score += 2
            
            total_score = keyword_score + pattern_score
            if total_score > 0:
                scores[intent] = total_score
        
        # Determine primary intent
        if not scores:
            primary_intent = "general_faq"
            confidence = 0.3
        else:
            primary_intent = max(scores, key=scores.get)
            max_score = scores[primary_intent]
            total_score = sum(scores.values())
            confidence = min(0.9, 0.4 + (max_score / max(total_score, 1)) * 0.5)
        
        # Get alternatives
        alternatives = [
            intent for intent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
            if intent != primary_intent
        ][:3]
        
        routing = INTENT_ROUTING_MAP.get(primary_intent, "knowledge_base")
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "intent": primary_intent,
                "routing": routing,
                "alternative_intents": alternatives,
                "all_scores": scores,
            },
            confidence=confidence,
            metadata={"classification_method": "rule_based"},
        )
    
    def _build_intent_keywords(self) -> Dict[str, List[str]]:
        """Build keyword dictionary for intents"""
        return {
            "appointment_booking": [
                "book", "booking", "schedule", "scheduling", "make appointment",
                "new appointment", "first appointment", "reserve", "arrange",
            ],
            "appointment_reschedule": [
                "reschedule", "rescheduling", "change appointment", "move appointment",
                "postpone", "change time", "different time", "rebook",
            ],
            "appointment_cancel": [
                "cancel", "cancelling", "cancellation", "cancel appointment",
                "remove appointment", "delete appointment",
            ],
            "clinic_information": [
                "where", "location", "address", "directions", "hours", "opening",
                "open", "close", "clinic info", "contact", "phone number", "email",
            ],
            "billing_query": [
                "bill", "billing", "payment", "pay", "cost", "price", "fee",
                "charge", "invoice", "statement", "balance",
            ],
            "insurance_query": [
                "insurance", "coverage", "covered", "in-network", "out-of-network",
                "copay", "deductible", "claim",
            ],
            "preparation_guidance": [
                "bring", "prepare", "preparation", "before appointment", "what to expect",
                "what should i know", "how to prepare",
            ],
            "policy_query": [
                "policy", "policies", "rules", "late arrival", "missed appointment",
                "no-show", "no show", "referral", "referrals",
            ],
            "general_faq": [
                "what", "how", "when", "who", "why", "can", "do you", "does",
            ],
            "medical_advice_request": [
                "symptom", "symptoms", "diagnosis", "diagnose", "treat", "treatment",
                "medication", "medicine", "prescription", "pain", "sick", "ill",
                "rash", "fever", "headache", "condition", "disease",
            ],
            "emergency": [
                "emergency", "urgent", "severe", "critical", "unconscious",
                "bleeding", "chest pain", "difficulty breathing", "stroke",
                "heart attack", "dying", "life threatening",
            ],
            "escalation_request": [
                "human", "agent", "representative", "staff", "person",
                "speak to someone", "talk to someone", "real person",
            ],
            "feedback": [
                "feedback", "complaint", "complain", "review", "suggestion",
                "thank you", "great", "terrible", "awful", "excellent",
            ],
            "out_of_scope": [
                "weather", "sports", "politics", "entertainment", "movie",
                "music", "game", "unrelated",
            ],
        }
    
    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for intents"""
        return {
            "appointment_booking": [
                r"i (?:want|need|would like) to (?:book|schedule|make)",
                r"can i (?:book|schedule|make) an appointment",
                r"how do i (?:book|schedule|make) an appointment",
            ],
            "appointment_reschedule": [
                r"i (?:want|need|would like) to (?:reschedule|change|move)",
                r"can i (?:reschedule|change|move) my appointment",
                r"(?:reschedule|change|move) my appointment",
            ],
            "appointment_cancel": [
                r"i (?:want|need|would like) to cancel",
                r"can i cancel my appointment",
                r"cancel my appointment",
            ],
            "clinic_information": [
                r"where (?:is|are) (?:you|your|the clinic)",
                r"what (?:are|is) your (?:hours|opening|address)",
                r"how do i (?:get to|find) (?:you|the clinic)",
            ],
            "medical_advice_request": [
                r"what should i (?:take|do) for",
                r"is (?:this|my) (?:rash|pain|symptom|condition)",
                r"should i (?:be worried|see a doctor) about",
                r"do i need (?:medication|antibiotics|treatment) for",
            ],
            "emergency": [
                r"i('m| am) having (?:chest pain|trouble breathing|a heart attack|a stroke)",
                r"(?:severe|extreme|unbearable) (?:pain|bleeding)",
                r"i think i('m| am) (?:dying|having a stroke|having a heart attack)",
            ],
            "escalation_request": [
                r"(?:speak|talk) to (?:a|an) (?:human|agent|representative|person)",
                r"can i (?:speak|talk) to (?:someone|a person)",
                r"i want (?:a|an) (?:human|agent|representative)",
            ],
        }