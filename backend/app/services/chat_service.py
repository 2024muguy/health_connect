"""
HealthConnect AI - Chat Service
================================
Business logic for chat and conversation management.

Features:
- Conversation lifecycle management
- Message processing
- Session management
- Conversation history
- Response generation pipeline
"""

import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from app.agents.orchestrator import Orchestrator
from app.agents.base_agent import AgentContext, AgentResult
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageSender, MessageType

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
from app.services.input_guard import guard_message  # noqa: E402
from app.services.audit_log import audit  # noqa: E402
from app.services.memory_service import memory_service  # noqa: E402
from app.services.uncertainty_service import uncertainty_service  # noqa: E402
from app.services.booking_service import booking_service  # noqa: E402

# Module-level state (persists across ChatService instances)
_PENDING_ESCALATIONS: dict = {}



# ============================================
# Response scrubber — belt-and-braces guard
# ============================================
# Even if a downstream generator leaks raw KB content, this scrubs it at
# the API boundary before the response is returned to the client.

_STRUCTURED_MARKERS = (
    "Variable:", "Data Type:", "Description:", "Example:", "Notes:",
)

_KB_ARTIFACT_MARKERS = (
    "Q: Can the assistant tell me",
    "A: This information assistant",
    "What to Bring to an Appointment",
    "7. What to Bring",
)

_SAFE_FALLBACK = (
    "I don't have a confident answer for that in HealthConnect's knowledge base. "
    "I can connect you with a HealthConnect staff member, or help you book "
    "a consultation. Which would you prefer?"
)

_SAFE_FOLLOWUP = (
    "Of course. To help with that, could you tell me a bit more about what "
    "you'd like to do next — book an appointment, reschedule an existing one, "
    "or ask about clinic services?"
)

_SHORT_FOLLOWUPS = {
    "yes", "yep", "yeah", "yup", "sure", "ok", "okay", "k",
    "no", "nope", "nah", "n",
    "please", "please do", "go ahead", "yes please",
    "sounds good", "alright", "fine",
}


def _is_short_followup(query: str) -> bool:
    if not query:
        return False
    q = query.strip().lower().rstrip(".!?,")
    return q in _SHORT_FOLLOWUPS


def _looks_like_leak(text: str) -> bool:
    """Detect raw KB chunk content that should not be shown to a patient."""
    if not text:
        return False
    # Structured data (data-dictionary rows)
    structured_hits = sum(1 for m in _STRUCTURED_MARKERS if m in text)
    if structured_hits >= 2:
        return True
    # Verbatim KB artefacts
    for marker in _KB_ARTIFACT_MARKERS:
        if marker in text:
            return True
    return False


def _scrub_response(text: str, query: str = "") -> str:
    """Return a safe, patient-friendly response. Replaces leaked KB content."""
    if not text or not text.strip():
        return _SAFE_FALLBACK
    if _looks_like_leak(text):
        logger.warning(f"Response scrubber triggered. Query={query!r}")
        if _is_short_followup(query):
            return _SAFE_FOLLOWUP
        return _SAFE_FALLBACK
    return text
settings = get_settings()


class ChatService:
    """
    Chat Service.
    Manages conversations and processes messages.
    """
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        
        # Register all agents
        from app.services.agent_setup import setup_agents
        setup_agents(self.orchestrator)
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.session_timeout = settings.safety.SESSION_TIMEOUT_MINUTES * 60
        logger.info("ChatService initialized")

    # ============================================
    # Database Persistence Helpers
    # ============================================


    @staticmethod
    def _map_service(service: str) -> str:
        """Map a human service name to the backend appointment_type enum."""
        s = (service or "").lower()
        if any(k in s for k in ("dermat", "cardio", "neuro", "ortho", "special")):
            return "specialist"
        if any(k in s for k in ("lab", "blood", "test")):
            return "lab"
        if any(k in s for k in ("imag", "mri", "xray", "x-ray", "ct", "scan")):
            return "imaging"
        if any(k in s for k in ("vaccin", "immuniz")):
            return "vaccination"
        if any(k in s for k in ("physical", "check")):
            return "physical"
        if any(k in s for k in ("consult", "internal", "medicine", "pediat", "gyn")):
            return "consultation"
        if any(k in s for k in ("urgent", "emergency")):
            return "urgent_care"
        if any(k in s for k in ("tele", "virtual", "online")):
            return "telehealth"
        if any(k in s for k in ("general", "outpatient", "primary")):
            return "general"
        return "general"

    async def _ensure_conversation_db(self, conversation_code: str, session_token=None, user_id=None) -> str:
        """Ensure a Conversation row exists in the DB and return its UUID."""
        import uuid
        from app.database.session import AsyncSessionLocal
        from app.models.conversation import Conversation, ConversationStatus
        from sqlalchemy import select

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Conversation).where(Conversation.conversation_code == conversation_code)
            )
            existing = result.scalar_one_or_none()
            if existing:
                return str(existing.id)

            # Also check by session_token to avoid UNIQUE violation
            if session_token:
                r2 = await session.execute(
                    select(Conversation).where(Conversation.session_token == session_token)
                )
                existing2 = r2.scalar_one_or_none()
                if existing2:
                    return str(existing2.id)

            conv = Conversation(
                conversation_code=conversation_code,
                session_token=session_token or str(uuid.uuid4()),
                status=ConversationStatus.ACTIVE,
                patient_id=None,
            )
            session.add(conv)
            await session.commit()
            await session.refresh(conv)
            return str(conv.id)

    async def _persist_message_db(
        self,
        conversation_code: str,
        role: str,
        content: str,
        intent=None,
        safety_category=None,
        session_token: Optional[str] = None,
    ) -> None:
        """Persist a single message to the DB."""
        from app.database.session import AsyncSessionLocal
        from app.models.message import Message, MessageSender, MessageType

        try:
            conv_uuid = await self._ensure_conversation_db(
                conversation_code, session_token=session_token
            )
            async with AsyncSessionLocal() as session:
                sender = MessageSender.USER if role == "user" else MessageSender.ASSISTANT
                msg = Message(
                    conversation_id=conv_uuid,
                    sender_type=sender,
                    message_type=MessageType.TEXT,
                    content=content,
                    intent=intent,
                    safety_category=safety_category,
                )
                session.add(msg)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist message: {e}")

    async def _load_history_db(self, conversation_code: str, limit: int = 50):
        """Load conversation history from DB."""
        try:
            from app.database.session import AsyncSessionLocal
            from app.models.conversation import Conversation
            from app.models.message import Message, MessageSender
            from sqlalchemy import select

            async with AsyncSessionLocal() as session:
                r = await session.execute(
                    select(Conversation).where(Conversation.conversation_code == conversation_code)
                )
                conv = r.scalar_one_or_none()
                if not conv:
                    return []

                msgs = await session.execute(
                    select(Message)
                    .where(Message.conversation_id == str(conv.id))
                    .order_by(Message.created_at.asc())
                    .limit(limit)
                )
                out = []
                for m in msgs.scalars().all():
                    role = "user" if m.sender_type == MessageSender.USER else "assistant"
                    out.append({
                        "id": str(m.id),
                        "role": role,
                        "content": m.content,
                        "timestamp": m.created_at.isoformat() if m.created_at else None,
                        "intent": m.intent,
                        "safety_category": m.safety_category,
                    })
                return out
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")
            return []


    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        session_token: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process incoming message and generate response.
        
        Args:
            message: User message
            conversation_id: Existing conversation ID
            session_token: Session token
            user_id: User identifier
            
        Returns:
            Dict: Response with metadata
        """
        # ---- Input guard (injection / size / sanitize) ----
        guard = guard_message(message)
        if not guard.allowed:
            logger.warning(f"Input guard rejected message (reason={guard.reason})")
            audit("input_blocked", reason=guard.reason, session=session_token, preview=message[:120])
            _blocked = (
                "I can't help with that request. I'm here for clinic "
                "information, appointments, and services. How can I help?"
            )
            return {
                "conversation_id": conversation_id or "",
                "text": _blocked,
                "message": _blocked,
                "response": _blocked,
                "intent": "blocked",
                "requires_human": False,
                "safety_category": "injection_blocked",
            }
        message = guard.sanitized or message

        # ---- Escalation intent short-circuit ----
        # Catch common phrasings that should hand off to a human even when
        # the LLM/router classifies them as something else.
        ESCALATION_PHRASES = (
            "connect me", "connecting me", "connect me with",
            "put me in touch", "put me through", "put me in contact",
            "speak to a human", "speak to someone", "speak to a person",
            "talk to a human", "talk to someone", "talk to a person",
            "speak to a staff member", "talk to a staff member",
            "speak to a representative", "talk to a representative",
            "speak to a manager", "talk to a manager",
            "speak with", "talk with", "chat with",
            "real person", "live agent", "human agent", "human please",
            "transfer me", "escalate", "raise a complaint",
            "isnt connecting", "arent connecting", "not connecting",
            "why arent you", "why are you not",
        )
        m_lower = message.lower()
        wants_human = any(phrase in m_lower for phrase in ESCALATION_PHRASES)

        # Follow-up confirmation of a prior escalation offer
        if not wants_human and session_token:
            if _PENDING_ESCALATIONS.get(session_token):
                if m_lower.strip().rstrip(".!?") in ("yes", "yep", "yeah", "sure", "ok", "okay", "please"):
                    wants_human = True

        if wants_human:
            logger.info(f"[ESCALATION] detected in message: {message!r}")
            # Mark a pending escalation for the next turn so a subsequent
            # "yes" also triggers
            _PENDING_ESCALATIONS[session_token] = True

            try:
                from app.services.tool_registry import tool_registry
                tool_result = await tool_registry.call(
                    "escalate_to_human",
                    reason=message,
                    session_token=session_token,
                )
            except Exception as e:
                logger.warning(f"escalate_to_human tool failed: {e}")
                tool_result = {"ok": False}

            pass  # keep pending flag so next 'yes' escalates too

            text = (
                "Understood — I'm connecting you with a HealthConnect staff member now. "
                "A representative will reach out shortly. You can also call the clinic "
                "directly during opening hours."
            )

            # If this turn was a bare confirmation of a prior escalation offer,
            # consume the pending flag so it doesn't linger forever.
            _bare_yes = m_lower.strip().rstrip(".!?").lower() in (
                "yes", "yep", "yeah", "sure", "ok", "okay", "please",
            )
            if _bare_yes:
                _PENDING_ESCALATIONS.pop(session_token, None)

            return {
                "conversation_id": "",
                "text": text,
                "message": text,
                "response": text,
                "intent": "escalation_request",
                "requires_human": True,
                "escalated": True,
                "tool_result": tool_result,
            }

        # ---- Hybrid conversational booking interception ----
        if booking_service.enabled and session_token:
            logger.info(
                f"[BOOKING] enabled={booking_service.enabled} "
                f"session={session_token[:20]}... "
                f"is_active={booking_service.is_active(session_token)} "
                f"message={message[:40]!r}"
            )
            try:
                if booking_service.is_active(session_token):
                    slots = booking_service.update_from_message(session_token, message)
                    logger.info(
                        f"[BOOKING] slots service={slots.service} "
                        f"date={slots.date} time={slots.time} "
                        f"confirmed={slots.confirmed} "
                        f"ready={booking_service.ready_to_book(slots)}"
                    )
                    if booking_service.ready_to_book(slots):
                        # Confirm + call the actual booking tool
                        from app.services.tool_registry import tool_registry
                        result = await tool_registry.call(
                            "create_appointment",
                            patient_id="237bde9c-ca35-46d1-8dcf-edb861583a98",
                            appointment_type=self._map_service(slots.service),
                            scheduled_datetime=f"{slots.date}T{slots.time}:00",
                            duration_minutes=30,
                            reason=slots.service,
                        )
                        booking_service.cancel(session_token)
                        if result.get("ok"):
                            apt = result["result"]
                            text = (
                                f"All set! I've booked your {slots.service} appointment "
                                f"on {slots.date} at {slots.time}. "
                                f"Your appointment code is {apt.get('appointment_code')}."
                            )
                        else:
                            text = (
                                "I couldn't complete the booking automatically. "
                                "Let me connect you with a staff member who can finish it."
                            )
                        return {
                            "conversation_id": "",
                            "text": text,
                            "message": text,
                            "response": text,
                            "intent": "appointment_booking",
                            "requires_human": not result.get("ok"),
                            "booking_completed": result.get("ok", False),
                        }
                    else:
                        # Ask for the next missing slot
                        prompt = booking_service.next_prompt(slots)
                        return {
                            "conversation_id": "",
                            "text": prompt,
                            "message": prompt,
                            "response": prompt,
                            "intent": "appointment_booking",
                            "requires_human": False,
                        }
                elif booking_service.detect_booking_intent(message):
                    booking_service.start(session_token)
                    slots = booking_service.update_from_message(session_token, message)
                    prompt = booking_service.next_prompt(slots)
                    return {
                        "conversation_id": "",
                        "text": prompt,
                        "message": prompt,
                        "response": prompt,
                        "intent": "appointment_booking",
                        "requires_human": False,
                    }
            except Exception as e:
                logger.warning(f"booking interception failed: {e}", exc_info=True)

        # Get or create conversation.
        # Priority: explicit conversation_id -> existing session_token -> new
        if conversation_id:
            conversation = await self._get_conversation(conversation_id)
            if conversation is None:
                conversation = await self._create_conversation(session_token, user_id)
        else:
            conversation = None
            # Reuse the conversation tied to this session_token, if any
            if session_token:
                from app.database.session import AsyncSessionLocal
                from app.models.conversation import Conversation as ConvModel
                from sqlalchemy import select as _select
                try:
                    async with AsyncSessionLocal() as _s:
                        _r = await _s.execute(
                            _select(ConvModel)
                            .where(ConvModel.session_token == session_token)
                            .order_by(ConvModel.started_at.desc())
                            .limit(1)
                        )
                        conversation = _r.scalar_one_or_none()
                except Exception as e:
                    logger.warning(f"session lookup failed: {e}")

            if conversation is None:
                conversation = await self._create_conversation(session_token, user_id)
        
        # Get conversation history from DB
        conv_code = conversation_id or (conversation.conversation_code if conversation else None)
        history = await self._load_history_db(conv_code) if conv_code else []
        
        # ---- Load conversation memory (summary + facts) ----
        memory = {"summary": None, "facts": None}
        try:
            if conversation is not None:
                memory = memory_service.load_memory(conversation)
            elif conv_code:
                # fall back: fetch fresh so we don't lose state
                from app.database.session import AsyncSessionLocal
                from app.models.conversation import Conversation as ConvModel
                from sqlalchemy import select as _select
                async with AsyncSessionLocal() as _s:
                    _r = await _s.execute(
                        _select(ConvModel).where(ConvModel.conversation_code == conv_code)
                    )
                    _conv = _r.scalar_one_or_none()
                    if _conv is not None:
                        conversation = _conv
                        memory = memory_service.load_memory(_conv)
        except Exception as e:
            logger.warning(f"Failed to load memory: {e}")

        memory_block = memory_service.build_prompt_block(
            summary=memory.get("summary"),
            facts=memory.get("facts"),
            history=history,
        )

        # Debug: confirm what we're sending
        logger.info(
            f"[MEMORY] conversation={conv_code} "
            f"summary_chars={len(memory.get('summary') or '')} "
            f"facts_keys={list((memory.get('facts') or {}).keys())} "
            f"block_chars={len(memory_block)}"
        )

        # Build agent context (with memory)
        context = AgentContext(
            conversation_id=conversation_id or conversation.conversation_code,
            query=message,
            user_id=user_id,
            history=history,
            metadata={
                "memory_block": memory_block,
                "facts": memory.get("facts") or {},
            },
        )
        logger.info(f"[MEMORY] context.metadata set? hasattr={hasattr(context, 'metadata')}")
        
        # Process through orchestrator
        result = await self.orchestrator.process_conversation(context)
        
        # Update history
        history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        history.append({
            "role": "assistant",
            "content": result.output.get("text", result.output.get("response", "")),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        # Trim history
        max_turns = settings.safety.MAX_CONVERSATION_TURNS
        if len(history) > max_turns * 2:
            history = history[-max_turns * 2:]
        
        self._conversation_history[conversation_id or conversation.conversation_code] = history
        
        # Get response text from orchestrator output
        response_text = (
            result.output.get("text") or
            result.output.get("response") or
            "I apologize, but I couldn't generate a response. Please try again."
        )

        # Belt-and-braces: scrub any leaked KB content before returning
        response_text = _scrub_response(response_text, query=message)

        # Uncertainty gate — replaces low-confidence responses with a safe template
        gate = uncertainty_service.score_and_gate(
            response_text=response_text,
            query=message,
            retrieved_chunks=result.output.get("retrieved_chunks", []) or [],
        )
        if gate.get("gated"):
            logger.info(
                f"Uncertainty gate triggered: "
                f"confidence={gate.get('confidence')} "
                f"retrieval={gate.get('retrieval_score')} "
                f"judge={gate.get('judge_score')}"
            )
        response_text = gate["response"]

        # Uncertainty gate — replaces low-confidence responses with a safe template
        gate = uncertainty_service.score_and_gate(
            response_text=response_text,
            query=message,
            retrieved_chunks=result.output.get("retrieved_chunks", []) or [],
        )
        if gate.get("gated"):
            logger.info(
                f"Uncertainty gate triggered: "
                f"confidence={gate.get('confidence')} "
                f"retrieval={gate.get('retrieval_score')} "
                f"judge={gate.get('judge_score')}"
            )
        response_text = gate["response"]
        
        # Build response with BOTH "text" and "message" keys for compatibility
        response = {
            "conversation_id": conversation_id or conversation.conversation_code,
            "text": response_text,
            "message": response_text,  # Keep for backwards compatibility
            "response": response_text,  # Support "response" key too
            "intent": result.output.get("intent", "unknown"),
            "intent_confidence": result.confidence,
            "safety_category": result.output.get("safety_category", "safe"),
            "safety_score": result.output.get("safety_score", 1.0),
            "requires_human": result.output.get("requires_human", False),
            "citations": result.output.get("citations", []),
            "action_performed": result.output.get("action_performed"),
            "processing_time_ms": result.execution_time_ms,
            "confidence": gate.get("confidence"),
            "retrieval_score": gate.get("retrieval_score"),
            "judge_score": gate.get("judge_score"),
            "uncertainty_gated": gate.get("gated", False),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Persist both messages to DB
        if conv_code:
            await self._persist_message_db(
                conv_code, "user", message, session_token=session_token
            )
            await self._persist_message_db(
                conv_code,
                "assistant",
                response_text,
                intent=response.get("intent"),
                safety_category=response.get("safety_category"),
                session_token=session_token,
            )

        # ---- Update rolling memory (summary + facts) ----
        try:
            if conv_code:
                await memory_service.update_memory(conv_code, history)
        except Exception as e:
            logger.warning(f"memory update failed: {e}")

        return response
    
    async def _create_conversation(
        self,
        session_token: Optional[str],
        user_id: Optional[str],
    ) -> Conversation:
        """Create new conversation and persist it to the DB.

        Idempotent by session_token: if a conversation already exists for
        this session, return it instead of inserting a duplicate.
        """
        session_token = session_token or str(uuid.uuid4())

        # Idempotency: check whether this session_token already has a row
        try:
            from app.database.session import AsyncSessionLocal
            from app.models.conversation import Conversation as ConvModel
            from sqlalchemy import select
            async with AsyncSessionLocal() as s:
                r = await s.execute(
                    select(ConvModel).where(ConvModel.session_token == session_token)
                )
                existing = r.scalar_one_or_none()
                if existing:
                    logger.info(
                        f"Reusing existing conversation {existing.conversation_code} "
                        f"(session={session_token})"
                    )
                    self._active_sessions[existing.conversation_code] = {
                        "created_at": datetime.now(timezone.utc),
                        "last_activity": datetime.now(timezone.utc),
                        "message_count": existing.message_count or 0,
                    }
                    return existing
        except Exception as e:
            logger.warning(f"session_token lookup failed: {e}")

        # Otherwise create a new conversation
        conversation_code = f"CONV-{uuid.uuid4().hex[:8].upper()}"
        conversation = Conversation(
            conversation_code=conversation_code,
            session_token=session_token,
            status=ConversationStatus.ACTIVE,
            patient_id=None,
        )

        try:
            from app.database.session import AsyncSessionLocal
            async with AsyncSessionLocal() as s:
                s.add(conversation)
                await s.commit()
                await s.refresh(conversation)
            logger.info(f"Created conversation: {conversation_code} (session={session_token})")
        except Exception as e:
            logger.warning(f"Failed to persist new conversation: {e}")

        self._active_sessions[conversation_code] = {
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "message_count": 0,
        }

        return conversation
    
    async def _get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get existing conversation"""
        # Check active sessions
        if conversation_id in self._active_sessions:
            self._active_sessions[conversation_id]["last_activity"] = datetime.now(timezone.utc)
            return Conversation(
                conversation_code=conversation_id,
                session_token="",
                status=ConversationStatus.ACTIVE,
            )
        
        return None
    
    async def end_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        End a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict: Result
        """
        if conversation_id in self._active_sessions:
            del self._active_sessions[conversation_id]
        
        if conversation_id in self._conversation_history:
            history = self._conversation_history.pop(conversation_id)
            return {
                "status": "ended",
                "conversation_id": conversation_id,
                "total_messages": len(history),
            }
        
        return {
            "status": "not_found",
            "conversation_id": conversation_id,
        }
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get conversation history from DB."""
        return await self._load_history_db(conversation_id, limit)


    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            int: Number of sessions cleaned
        """
        now = datetime.now(timezone.utc)
        expired_ids = []
        
        for conversation_id, session_data in self._active_sessions.items():
            last_activity = session_data.get("last_activity")
            
            if last_activity:
                elapsed = (now - last_activity).total_seconds()
                if elapsed > self.session_timeout:
                    expired_ids.append(conversation_id)
        
        for conversation_id in expired_ids:
            del self._active_sessions[conversation_id]
            self._conversation_history.pop(conversation_id, None)
        
        logger.info(f"Cleaned up {len(expired_ids)} expired sessions")
        return len(expired_ids)
    
    async def get_active_conversations(self) -> List[Dict[str, Any]]:
        """Get active conversations"""
        return [
            {
                "conversation_id": cid,
                "message_count": data.get("message_count", 0),
                "created_at": data.get("created_at", "").isoformat(),
                "last_activity": data.get("last_activity", "").isoformat(),
            }
            for cid, data in self._active_sessions.items()
        ]