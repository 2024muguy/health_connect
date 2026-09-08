"""
HealthConnect AI - Message Bus
================================
Inter-agent communication system.

Features:
- Asynchronous message passing
- Pub/sub pattern
- Message queuing
- Correlation tracking
- Message history
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Awaitable
from enum import Enum
from datetime import datetime, timezone

from config.logging_config import get_logger

logger = get_logger(__name__)


class MessageType(Enum):
    """Message type enumeration"""
    QUERY = "query"
    RESPONSE = "response"
    CONTEXT = "context"
    SAFETY_ALERT = "safety_alert"
    ACTION_REQUEST = "action_request"
    ACTION_CONFIRMATION = "action_confirmation"
    ERROR = "error"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"


class MessagePriority(Enum):
    """Message priority enumeration"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentMessage:
    """
    Message passed between agents.
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""
    message_type: MessageType = MessageType.QUERY
    content: Any = None
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class MessageBus:
    """
    Asynchronous message bus for inter-agent communication.
    
    Features:
    - Topic-based pub/sub
    - Direct messaging
    - Message history
    - Priority queue
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[AgentMessage], Awaitable[None]]]] = {}
        self._message_history: List[AgentMessage] = []
        self._max_history = 1000
        self._correlation_map: Dict[str, List[AgentMessage]] = {}
        logger.info("MessageBus initialized")
    
    async def publish(self, message: AgentMessage) -> None:
        """
        Publish message to subscribers.
        
        Args:
            message: Message to publish
        """
        # Store in history
        self._store_message(message)
        
        # Notify subscribers
        subscribers = self._subscribers.get(message.receiver, [])
        subscribers.extend(self._subscribers.get("*", []))
        
        for subscriber in subscribers:
            try:
                await subscriber(message)
            except Exception as e:
                logger.error(f"Subscriber error for {message.receiver}: {e}")
        
        logger.debug(
            f"Published message {message.message_id} "
            f"from {message.sender} to {message.receiver}"
        )
    
    async def send(
        self,
        message: AgentMessage,
        timeout: float = 30.0,
    ) -> Optional[AgentMessage]:
        """
        Send message and wait for response.
        
        Args:
            message: Message to send
            timeout: Response timeout in seconds
            
        Returns:
            Optional[AgentMessage]: Response message
        """
        # Create response queue
        response_queue = asyncio.Queue()
        correlation_id = message.message_id
        
        async def response_handler(response: AgentMessage):
            if response.correlation_id == correlation_id:
                await response_queue.put(response)
        
        # Subscribe for response
        response_topic = f"response:{message.sender}"
        self._subscribers.setdefault(response_topic, []).append(response_handler)
        
        try:
            # Send message
            await self.publish(message)
            
            # Wait for response
            response = await asyncio.wait_for(
                response_queue.get(),
                timeout=timeout,
            )
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Message {message.message_id} timed out")
            return None
        
        finally:
            # Clean up subscriber
            if response_topic in self._subscribers:
                self._subscribers[response_topic].remove(response_handler)
    
    def subscribe(
        self,
        topic: str,
        handler: Callable[[AgentMessage], Awaitable[None]],
    ) -> None:
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to
            handler: Message handler function
        """
        self._subscribers.setdefault(topic, []).append(handler)
        logger.debug(f"Subscribed to topic: {topic}")
    
    def unsubscribe(
        self,
        topic: str,
        handler: Callable[[AgentMessage], Awaitable[None]],
    ) -> None:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            handler: Handler to remove
        """
        if topic in self._subscribers and handler in self._subscribers[topic]:
            self._subscribers[topic].remove(handler)
            logger.debug(f"Unsubscribed from topic: {topic}")
    
    def _store_message(self, message: AgentMessage) -> None:
        """Store message in history"""
        self._message_history.append(message)
        
        # Trim history
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]
        
        # Track correlation
        if message.correlation_id:
            self._correlation_map.setdefault(message.correlation_id, []).append(message)
    
    def get_history(
        self,
        limit: int = 100,
        message_type: Optional[MessageType] = None,
    ) -> List[AgentMessage]:
        """
        Get message history.
        
        Args:
            limit: Maximum messages to return
            message_type: Filter by type
            
        Returns:
            List[AgentMessage]: Message history
        """
        history = self._message_history
        
        if message_type:
            history = [m for m in history if m.message_type == message_type]
        
        return history[-limit:]
    
    def get_correlated_messages(self, correlation_id: str) -> List[AgentMessage]:
        """Get messages with correlation ID"""
        return self._correlation_map.get(correlation_id, [])
    
    def clear_history(self) -> None:
        """Clear message history"""
        self._message_history = []
        self._correlation_map = {}
        logger.info("Message history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            "total_messages": len(self._message_history),
            "total_subscribers": sum(len(v) for v in self._subscribers.values()),
            "total_topics": len(self._subscribers),
            "total_correlations": len(self._correlation_map),
        }