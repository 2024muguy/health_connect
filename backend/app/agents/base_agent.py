"""
HealthConnect AI - Base Agent
===============================
Abstract base class for all agents.

Features:
- Agent lifecycle management
- Context handling
- Result standardization
- Error handling
- Performance tracking
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from config.logging_config import get_logger

logger = get_logger(__name__)


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


class AgentType(Enum):
    """Agent type enumeration"""
    ORCHESTRATOR = "orchestrator"
    INTENT_ROUTER = "intent_router"
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    ACTION = "action"
    SAFETY = "safety"
    COMPLIANCE = "compliance"
    EMERGENCY = "emergency"
    SUMMARY = "summary"
    FEEDBACK = "feedback"
    ANALYTICS = "analytics"


@dataclass
class AgentContext:
    """
    Context for agent execution.
    Contains all information needed for agent processing.
    """
    conversation_id: str
    query: str
    user_id: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    intent: Optional[str] = None
    safety_flags: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "conversation_id": self.conversation_id,
            "query": self.query,
            "user_id": self.user_id,
            "history": self.history,
            "retrieved_chunks": self.retrieved_chunks,
            "intent": self.intent,
            "safety_flags": self.safety_flags,
            "metadata": self.metadata,
        }


@dataclass
class AgentResult:
    """
    Standardized agent execution result.
    """
    agent_type: AgentType
    status: AgentStatus
    output: Any = None
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.status == AgentStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if execution failed"""
        return self.status in [AgentStatus.FAILED, AgentStatus.BLOCKED, AgentStatus.TIMEOUT]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "output": self.output,
            "confidence": self.confidence,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    All agents must implement:
    - execute(): Main agent logic
    - validate_context(): Validate input context
    - handle_error(): Handle execution errors
    """
    
    def __init__(
        self,
        agent_type: AgentType,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.agent_type = agent_type
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.agent_id = str(uuid.uuid4())
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._error_count = 0
        
        # Optional dependencies
        self.llm_provider = None
        self.vector_store = None
        self.cache_manager = None
        
        logger.info(f"Initialized {agent_type.value} agent (ID: {self.agent_id})")
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute agent logic.
        
        Args:
            context: Agent execution context
            
        Returns:
            AgentResult: Execution result
        """
        pass
    
    def validate_context(self, context: AgentContext) -> bool:
        """
        Validate agent context before execution.
        
        Args:
            context: Agent context
            
        Returns:
            bool: True if valid
        """
        if not context.query:
            logger.error(f"{self.agent_type.value} agent: Empty query")
            return False
        
        if not context.conversation_id:
            logger.error(f"{self.agent_type.value} agent: Missing conversation ID")
            return False
        
        return True
    
    async def run(self, context: AgentContext) -> AgentResult:
        """
        Run agent with error handling and performance tracking.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Execution result
        """
        start_time = time.time()
        self.status = AgentStatus.RUNNING
        
        try:
            # Validate context
            if not self.validate_context(context):
                return AgentResult(
                    agent_type=self.agent_type,
                    status=AgentStatus.FAILED,
                    error="Invalid context",
                    agent_id=self.agent_id,
                )
            
            # Execute agent logic
            result = await self.execute(context)
            
            # Update statistics
            self._execution_count += 1
            self._total_execution_time += (time.time() - start_time) * 1000
            
            self.status = AgentStatus.COMPLETED if result.is_successful else result.status
            
            return result
            
        except asyncio.TimeoutError:
            self.status = AgentStatus.TIMEOUT
            self._error_count += 1
            logger.error(f"{self.agent_type.value} agent timed out")
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.TIMEOUT,
                error="Execution timed out",
                agent_id=self.agent_id,
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            self._error_count += 1
            logger.error(f"{self.agent_type.value} agent failed: {e}", exc_info=True)
            return self.handle_error(context, e)
    
    def handle_error(
        self,
        context: AgentContext,
        error: Exception,
    ) -> AgentResult:
        """
        Handle execution errors.
        Can be overridden by subclasses for custom error handling.
        
        Args:
            context: Agent context
            error: Exception
            
        Returns:
            AgentResult: Error result
        """
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.FAILED,
            error=str(error),
            agent_id=self.agent_id,
        )
    
    async def run_with_timeout(
        self,
        context: AgentContext,
        timeout_seconds: float = 30.0,
    ) -> AgentResult:
        """
        Run agent with timeout.
        
        Args:
            context: Agent context
            timeout_seconds: Timeout in seconds
            
        Returns:
            AgentResult: Execution result
        """
        try:
            return await asyncio.wait_for(
                self.run(context),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.TIMEOUT,
                error=f"Timeout after {timeout_seconds}s",
                agent_id=self.agent_id,
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "execution_count": self._execution_count,
            "total_execution_time_ms": self._total_execution_time,
            "average_execution_time_ms": (
                self._total_execution_time / self._execution_count
                if self._execution_count > 0 else 0
            ),
            "error_count": self._error_count,
        }
    
    def set_llm_provider(self, provider: Any) -> None:
        """Set LLM provider"""
        self.llm_provider = provider
    
    def set_vector_store(self, vector_store: Any) -> None:
        """Set vector store"""
        self.vector_store = vector_store
    
    def set_cache_manager(self, cache_manager: Any) -> None:
        """Set cache manager"""
        self.cache_manager = cache_manager
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type.value})>"