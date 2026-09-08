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
settings = get_settings()


class ChatService:
    """
    Chat Service.
    Manages conversations and processes messages.
    """
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.session_timeout = settings.safety.SESSION_TIMEOUT_MINUTES * 60
        logger.info("ChatService initialized")
    
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
        # Get or create conversation
        if conversation_id:
            conversation = await self._get_conversation(conversation_id)
        else:
            conversation = await self._create_conversation(session_token, user_id)
        
        # Get conversation history
        history = self._conversation_history.get(
            conversation_id,
            [],
        )
        
        # Build agent context
        context = AgentContext(
            conversation_id=conversation_id or conversation.conversation_code,
            query=message,
            user_id=user_id,
            history=history,
        )
        
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
            "content": result.output.get("text", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        # Trim history
        max_turns = settings.safety.MAX_CONVERSATION_TURNS
        if len(history) > max_turns * 2:
            history = history[-max_turns * 2:]
        
        self._conversation_history[conversation_id or conversation.conversation_code] = history
        
        # Build response
        response = {
            "conversation_id": conversation_id or conversation.conversation_code,
            "message": result.output.get("text", ""),
            "intent": result.output.get("intent", "unknown"),
            "intent_confidence": result.confidence,
            "safety_category": result.output.get("safety_category", "safe"),
            "requires_human": result.output.get("requires_human", False),
            "citations": result.output.get("citations", []),
            "action_performed": result.output.get("action_performed"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        return response
    
    async def _create_conversation(
        self,
        session_token: Optional[str],
        user_id: Optional[str],
    ) -> Conversation:
        """Create new conversation"""
        conversation_code = f"CONV-{uuid.uuid4().hex[:8].upper()}"
        session_token = session_token or str(uuid.uuid4())
        
        conversation = Conversation(
            conversation_code=conversation_code,
            session_token=session_token,
            status=ConversationStatus.ACTIVE,
            patient_id=None,  # Would be set if user is authenticated
        )
        
        self._active_sessions[conversation_code] = {
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "message_count": 0,
        }
        
        logger.info(f"Created conversation: {conversation_code}")
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
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum messages
            
        Returns:
            List[Dict]: Conversation history
        """
        history = self._conversation_history.get(conversation_id, [])
        return history[-limit:]
    
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