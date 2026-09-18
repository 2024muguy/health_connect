"""
HealthConnect AI - Orchestrator
================================
Main orchestrator for coordinating all agents.

Features:
- Agent lifecycle management
- Conversation pipeline
- Safety-first processing
- Error recovery
- Performance monitoring
"""

import asyncio
import time
import uuid
from typing import Optional, List, Dict, Any
from enum import Enum

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)
from app.agents.message_bus import MessageBus, AgentMessage, MessageType, MessagePriority

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PipelineStage(Enum):
    """Conversation pipeline stages"""
    INTENT_ROUTING = "intent_routing"
    SAFETY_CHECK = "safety_check"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    RESPONSE_GENERATION = "response_generation"
    ACTION_EXECUTION = "action_execution"
    RESPONSE_ASSEMBLY = "response_assembly"


class Orchestrator:
    """
    Main orchestrator for the multi-agent system.
    Coordinates all agents through the conversation pipeline.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.message_bus = MessageBus()
        self._pipeline_results: Dict[str, Dict[str, Any]] = {}
        self._conversation_start_times: Dict[str, float] = {}
        
        # Initialize LLM provider for agents
        try:
            from app.llm.groq_provider import GroqProvider
            from app.llm.base import LLMConfig
            
            config = LLMConfig(
                provider="groq",
                api_key=settings.groq.API_KEY,
                model=settings.groq.MODEL,
                max_tokens=settings.groq.MAX_TOKENS,
                temperature=settings.groq.TEMPERATURE,
                timeout=60,
            )
            self.llm_provider = GroqProvider(config)
            logger.info("✅ Groq provider initialized for orchestrator")
        except Exception as e:
            logger.warning(f"Groq provider init failed: {e}")
            self.llm_provider = None
        
        logger.info("Orchestrator initialized")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent to register
        """
        # Set LLM provider if available
        if hasattr(self, 'llm_provider') and self.llm_provider:
            agent.set_llm_provider(self.llm_provider)
        
        self.agents[agent.agent_type] = agent
        logger.info(f"Registered agent: {agent.agent_type.value}")
    
    def register_agents(self, agents: List[BaseAgent]) -> None:
        """Register multiple agents"""
        for agent in agents:
            self.register_agent(agent)
    
    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """Get agent by type"""
        return self.agents.get(agent_type)
    
    async def process_conversation(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Process a complete conversation through the pipeline.
        
        Pipeline:
        1. Intent Routing
        2. Safety Check (Pre-generation)
        3. Knowledge Retrieval
        4. Response Generation
        5. Action Execution (if needed)
        6. Response Assembly
        
        Args:
            context: Conversation context
            
        Returns:
            AgentResult: Final response
        """
        conversation_start = time.time()
        self._conversation_start_times[context.conversation_id] = conversation_start
        
        logger.info(f"Processing conversation: {context.conversation_id}")
        logger.info(f"Query: '{context.query[:100]}...'")
        
        pipeline_results = {}
        
        # ============================================
        # Stage 1: Intent Routing
        # ============================================
        intent_result = await self._stage_intent_routing(context)
        pipeline_results[PipelineStage.INTENT_ROUTING] = intent_result
        
        if intent_result.is_failed:
            return self._fallback_response(context, "Intent routing failed")
        
        # Update context with intent
        context.intent = intent_result.output.get("intent")
        
        # ============================================
        # Stage 2: Safety Check (Pre-generation)
        # ============================================
        safety_result = await self._stage_safety_check(context)
        pipeline_results[PipelineStage.SAFETY_CHECK] = safety_result
        
        if safety_result.status == AgentStatus.BLOCKED:
            return self._safety_block_response(context, safety_result)
        
        # Check for emergency
        if safety_result.output.get("action") == "emergency_protocol":
            return self._emergency_response(context, safety_result)
        
        # ============================================
        # Stage 3: Knowledge Retrieval
        # ============================================
        retrieval_result = await self._stage_knowledge_retrieval(context)
        pipeline_results[PipelineStage.KNOWLEDGE_RETRIEVAL] = retrieval_result
        
        # Update context with retrieved chunks
        if retrieval_result.is_successful:
            context.retrieved_chunks = retrieval_result.output.get("chunks", [])
        
        # ============================================
        # Stage 4: Response Generation
        # ============================================
        generation_result = await self._stage_response_generation(context)
        pipeline_results[PipelineStage.RESPONSE_GENERATION] = generation_result
        
        if generation_result.is_failed:
            return self._fallback_response(context, "Response generation failed")
        
        # ============================================
        # Stage 5: Action Execution (if needed)
        # ============================================
        action_result = await self._stage_action_execution(context, intent_result)
        pipeline_results[PipelineStage.ACTION_EXECUTION] = action_result
        
        # ============================================
        # Stage 6: Response Assembly
        # ============================================
        final_result = self._assemble_response(
            context=context,
            intent_result=intent_result,
            safety_result=safety_result,
            retrieval_result=retrieval_result,
            generation_result=generation_result,
            action_result=action_result,
        )
        
        # Store pipeline results (handle None results)
        self._pipeline_results[context.conversation_id] = {
            stage.value: result.to_dict() if result else None
            for stage, result in pipeline_results.items()
        }
        
        total_time = (time.time() - conversation_start) * 1000
        final_result.metadata["total_pipeline_time_ms"] = total_time
        final_result.metadata["pipeline_stages"] = list(pipeline_results.keys())
        
        logger.info(
            f"Conversation {context.conversation_id} completed in {total_time:.0f}ms"
        )
        
        return final_result
    
    async def _stage_intent_routing(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """Stage 1: Intent Routing"""
        agent = self.get_agent(AgentType.INTENT_ROUTER)
        
        if not agent:
            return AgentResult(
                agent_type=AgentType.INTENT_ROUTER,
                status=AgentStatus.FAILED,
                error="Intent router not registered",
            )
        
        return await agent.run_with_timeout(context, timeout_seconds=10.0)
    
    async def _stage_safety_check(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """Stage 2: Safety Check"""
        agent = self.get_agent(AgentType.SAFETY)
        
        if not agent:
            logger.warning("Safety agent not registered, skipping check")
            return AgentResult(
                agent_type=AgentType.SAFETY,
                status=AgentStatus.COMPLETED,
                output={"action": "allow", "safety_category": "safe"},
                confidence=1.0,
            )
        
        return await agent.run_with_timeout(context, timeout_seconds=5.0)
    
    async def _stage_knowledge_retrieval(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """Stage 3: Knowledge Retrieval"""
        _SHORT = {
            "yes", "yep", "yeah", "yup", "sure", "ok", "okay", "k",
            "no", "nope", "nah", "n",
            "please", "please do", "go ahead", "yes please",
            "sounds good", "alright", "fine",
        }
        q = (context.query or "").strip().lower().rstrip(".!?,")
        if q in _SHORT:
            logger.info(f"Skipping retrieval for short follow-up: {context.query!r}")
            return AgentResult(
                agent_type=AgentType.KNOWLEDGE,
                status=AgentStatus.COMPLETED,
                output={"chunks": [], "sources": []},
                confidence=0.0,
            )

        agent = self.get_agent(AgentType.KNOWLEDGE)
        
        if not agent:
            return AgentResult(
                agent_type=AgentType.KNOWLEDGE,
                status=AgentStatus.COMPLETED,
                output={"chunks": [], "sources": []},
                confidence=0.0,
            )
        
        return await agent.run_with_timeout(context, timeout_seconds=15.0)
    
    async def _stage_response_generation(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """Stage 4: Response Generation"""
        agent = self.get_agent(AgentType.CONVERSATION)
        
        if not agent:
            return AgentResult(
                agent_type=AgentType.CONVERSATION,
                status=AgentStatus.FAILED,
                error="Conversation agent not registered",
            )
        
        return await agent.run_with_timeout(context, timeout_seconds=30.0)
    
    async def _stage_action_execution(
        self,
        context: AgentContext,
        intent_result: AgentResult,
    ) -> Optional[AgentResult]:
        """Stage 5: Action Execution"""
        agent = self.get_agent(AgentType.ACTION)
        
        if not agent:
            return None
        
        # Only execute actions for certain intents
        intent = intent_result.output.get("intent", "")
        action_intents = [
            "appointment_booking",
            "appointment_reschedule",
            "appointment_cancel",
        ]
        
        if intent not in action_intents:
            return None
        
        return await agent.run_with_timeout(context, timeout_seconds=15.0)
    
    def _assemble_response(
        self,
        context: AgentContext,
        intent_result: AgentResult,
        safety_result: AgentResult,
        retrieval_result: AgentResult,
        generation_result: AgentResult,
        action_result: Optional[AgentResult],
    ) -> AgentResult:
        """Stage 6: Assemble final response"""
        final_intent = intent_result.output.get("intent", "unknown")
        response_text = generation_result.output.get("response", "")

        # --- Week 6 improvement: force human handoff for escalation intents ---
        ESCALATION_INTENTS = {"escalation_request", "feedback", "complaint"}
        DISPUTE_KEYWORDS = (
            "charged incorrectly", "wrong bill", "incorrect charge",
            "refund", "overcharged", "billing error", "dispute",
        )
        is_dispute = (
            final_intent == "billing_query"
            and any(k in (context.query or "").lower() for k in DISPUTE_KEYWORDS)
        )
        force_human = (final_intent in ESCALATION_INTENTS) or is_dispute

        # If escalation is required and the LLM didn't already produce
        # an escalation-style message, replace the response.
        ESCALATION_LANGUAGE = (
            "human", "agent", "representative", "staff member",
            "team member", "transfer", "escalat", "connect you",
        )
        if force_human and not any(k in response_text.lower() for k in ESCALATION_LANGUAGE):
            response_text = (
                "I understand \u2014 let me connect you with a HealthConnect staff member "
                "who can help with this directly. A representative will reach out shortly. "
                "You can also call the clinic directly during opening hours."
            )

        response_data = {
            "text": response_text,
            "intent": final_intent,
            "intent_confidence": intent_result.confidence,
            "safety_category": safety_result.output.get("safety_category", "safe"),
            "safety_score": safety_result.output.get("safety_score", 1.0),
            "retrieved_chunks": retrieval_result.output.get("chunks", []),
            "sources": retrieval_result.output.get("sources", []),
            "citations": generation_result.output.get("citations", []),
            "action_performed": action_result.output if action_result else None,
            "requires_human": (
                True if force_human else (
                    action_result.output.get("requires_human", False)
                    if action_result else False
                )
            ),
        }
        
        overall_confidence = self._calculate_overall_confidence([
            intent_result.confidence,
            safety_result.confidence,
            generation_result.confidence,
            retrieval_result.confidence,
        ])
        
        return AgentResult(
            agent_type=AgentType.ORCHESTRATOR,
            status=AgentStatus.COMPLETED,
            output=response_data,
            confidence=overall_confidence,
        )
    
    def _calculate_overall_confidence(self, confidences: List[float]) -> float:
        """Calculate weighted average confidence"""
        weights = [0.2, 0.2, 0.4, 0.2]  # Generation weighted highest
        valid_confidences = [c for c in confidences if c > 0]
        
        if not valid_confidences:
            return 0.0
        
        if len(valid_confidences) == len(confidences):
            return sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
        
        return sum(valid_confidences) / len(valid_confidences)
    
    def _fallback_response(
        self,
        context: AgentContext,
        reason: str,
    ) -> AgentResult:
        """Generate fallback response"""
        fallback_text = (
            "I apologize, but I'm having difficulty processing your request right now. "
            "Please try again in a moment, or contact our clinic directly for assistance."
        )
        
        return AgentResult(
            agent_type=AgentType.ORCHESTRATOR,
            status=AgentStatus.COMPLETED,
            output={
                "text": fallback_text,
                "intent": "fallback",
                "intent_confidence": 0.0,
                "safety_category": "safe",
                "safety_score": 1.0,
                "retrieved_chunks": [],
                "sources": [],
                "requires_human": True,
                "fallback_reason": reason,
            },
            confidence=0.0,
            metadata={"fallback": True, "reason": reason},
        )
    
    def _safety_block_response(
        self,
        context: AgentContext,
        safety_result: AgentResult,
    ) -> AgentResult:
        """Generate safety block response"""
        safety_category = safety_result.output.get("safety_category", "unknown")
        
        block_messages = {
            "emergency": (
                "\u26a0\ufe0f This may be a medical emergency.\n\n"
                "Please call 911 (or 999 / 112 in your region) or go to the nearest "
                "emergency room right away. Do not wait for a response from this assistant.\n\n"
                "For non-emergency urgent care, you can contact HealthConnect Clinic's "
                "urgent care line during opening hours."
            ),
            "medical_advice_request": (
                "I can't give medical advice or diagnose symptoms — that needs a "
                "clinician who knows your situation.\n\n"
                "What I can do:\n"
                "\u2022 Book a consultation with a HealthConnect clinician\n"
                "\u2022 Share clinic hours, services, and locations\n\n"
                "If this feels urgent or time-sensitive (for example labor, severe pain, "
                "difficulty breathing, or sudden symptoms), please call HealthConnect "
                "Clinic directly or call 911 / 999 / 112 if it's an emergency.\n\n"
                "Would you like help booking an appointment?"
            ),
            "pii_request": (
                "I can't access or share personal or medical records through this "
                "assistant. For anything involving your personal information, please "
                "contact HealthConnect Clinic directly and they'll be glad to help.\n\n"
                "Is there anything else I can help you with in the meantime?"
            ),
            "abusive_language": (
                "I'm here to help with clinic information and appointment tasks. "
                "Let me know how I can assist you."
            ),
            "out_of_scope": (
                "HealthConnect's assistant doesn't cover that topic, and I'm not able "
                "to give medical advice about specific conditions. For any concern "
                "about a specific condition, please:\n\n"
                "\u2022 Book a consultation with a HealthConnect clinician\n"
                "\u2022 In an emergency, call 911 / 999 / 112 immediately\n\n"
                "Would you like help booking an appointment?"
            ),
        }
        
        response_text = block_messages.get(
            safety_category,
            "I apologize, but I'm not able to help with that request. "
            "Would you like help with appointment scheduling or other administrative tasks?",
        )
        
        return AgentResult(
            agent_type=AgentType.ORCHESTRATOR,
            status=AgentStatus.BLOCKED,
            output={
                "text": response_text,
                "intent": "blocked",
                "safety_category": safety_category,
                "safety_score": 0.0,
                "requires_human": True,
            },
            confidence=1.0,
            metadata={"blocked": True, "safety_category": safety_category},
        )
    
    def _emergency_response(
        self,
        context: AgentContext,
        safety_result: AgentResult,
    ) -> AgentResult:
        """Generate emergency response"""
        emergency_text = (
            "IMPORTANT: If you are experiencing a medical emergency, "
            "please call 911 (or your local emergency number) immediately. "
            "Do not wait for a response from this assistant.\n\n"
            "For non-emergency urgent care, please contact HealthConnect Clinic's "
            "urgent care line during business hours."
        )
        
        return AgentResult(
            agent_type=AgentType.ORCHESTRATOR,
            status=AgentStatus.BLOCKED,
            output={
                "text": emergency_text,
                "intent": "emergency",
                "safety_category": "emergency",
                "safety_score": 0.0,
                "requires_human": True,
            },
            confidence=1.0,
            metadata={"emergency": True},
        )
    
    def get_pipeline_results(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline results for a conversation"""
        return self._pipeline_results.get(conversation_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "registered_agents": len(self.agents),
            "agent_details": {
                agent_type.value: agent.get_stats()
                for agent_type, agent in self.agents.items()
            },
            "message_bus": self.message_bus.get_stats(),
            "active_conversations": len(self._conversation_start_times),
        }