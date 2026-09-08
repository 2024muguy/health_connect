"""
HealthConnect AI - Base LLM Provider
=====================================
Abstract base class for all LLM providers.

Features:
- Unified interface
- Response standardization
- Error handling
- Retry logic
- Token counting
"""

import asyncio
import time
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, AsyncGenerator, Union
from enum import Enum

from config.logging_config import get_logger
from config.constants import LLM_PROVIDERS

logger = get_logger(__name__)


class LLMProviderType(Enum):
    """LLM provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class LLMConfig:
    """LLM provider configuration"""
    
    provider: str
    model: str
    api_key: str = ""
    max_tokens: int = 2048
    temperature: float = 0.3
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "provider": self.provider,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop_sequences": self.stop_sequences,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }


@dataclass
class LLMMessage:
    """LLM message"""
    
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    
    text: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    finish_reason: str = "stop"
    raw_response: Any = None
    request_id: Optional[str] = None
    
    @property
    def total_cost(self) -> float:
        """Calculate estimated cost"""
        # Cost per 1K tokens (approximate)
        cost_map = {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
            "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
            "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
            "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
            "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
            "gemini-pro": {"prompt": 0.000125, "completion": 0.000375},
        }
        
        costs = cost_map.get(self.model, {"prompt": 0.0, "completion": 0.0})
        prompt_cost = (self.prompt_tokens / 1000) * costs["prompt"]
        completion_cost = (self.completion_tokens / 1000) * costs["completion"]
        
        return prompt_cost + completion_cost
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "finish_reason": self.finish_reason,
            "request_id": self.request_id,
            "estimated_cost": self.total_cost,
        }


class LLMError(Exception):
    """LLM provider error"""
    
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        error_type: str = "general",
        retryable: bool = False,
        details: Optional[Dict] = None,
    ):
        self.message = message
        self.provider = provider
        self.error_type = error_type
        self.retryable = retryable
        self.details = details or {}
        super().__init__(self.message)


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All providers must implement:
    - generate(): Generate text from messages
    - generate_stream(): Stream text generation
    - count_tokens(): Count tokens in text
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider_name = config.provider
        self.model = config.model
        self._request_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        self._cache = {}
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text from messages.
        
        Args:
            messages: List of messages
            **kwargs: Additional generation parameters
            
        Returns:
            LLMResponse: Standardized response
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Stream text generation.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Yields:
            str: Text chunks
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count
            
        Returns:
            int: Token count
        """
        pass
    
    async def generate_with_retry(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """
        Generate with retry logic.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse: Response
        """
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = await self.generate(messages, **kwargs)
                self._update_stats(response)
                return response
            except LLMError as e:
                last_error = e
                
                if not e.retryable:
                    logger.error(f"Non-retryable LLM error: {e.message}")
                    raise
                
                wait_time = self.config.retry_delay * (2 ** attempt)
                logger.warning(
                    f"LLM error (attempt {attempt + 1}/{self.config.max_retries}): "
                    f"{e.message}. Retrying in {wait_time}s"
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                last_error = LLMError(
                    message=str(e),
                    provider=self.provider_name,
                    error_type="unknown",
                    retryable=True,
                )
                wait_time = self.config.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Unexpected LLM error (attempt {attempt + 1}/{self.config.max_retries}): "
                    f"{str(e)}. Retrying in {wait_time}s"
                )
                await asyncio.sleep(wait_time)
        
        raise LLMError(
            message=f"All retries failed: {last_error.message if last_error else 'Unknown error'}",
            provider=self.provider_name,
            error_type="max_retries_exceeded",
            retryable=False,
        )
    
    def _update_stats(self, response: LLMResponse) -> None:
        """Update internal statistics"""
        self._request_count += 1
        self._total_tokens += response.total_tokens
        self._total_cost += response.total_cost
    
    def _get_cache_key(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate cache key for messages"""
        key_parts = [self.provider_name, self.model]
        for msg in messages:
            key_parts.append(f"{msg.role}:{msg.content}")
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key = "|".join(key_parts)
        return hashlib.sha256(key.encode()).hexdigest()
    
    async def get_cached_response(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> Optional[LLMResponse]:
        """Get cached response if available"""
        cache_key = self._get_cache_key(messages, **kwargs)
        return self._cache.get(cache_key)
    
    async def cache_response(
        self,
        messages: List[LLMMessage],
        response: LLMResponse,
        **kwargs,
    ) -> None:
        """Cache a response"""
        cache_key = self._get_cache_key(messages, **kwargs)
        self._cache[cache_key] = response
        
        # Limit cache size
        if len(self._cache) > 1000:
            # Remove oldest entries
            for key in list(self._cache.keys())[:500]:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            "provider": self.provider_name,
            "model": self.model,
            "request_count": self._request_count,
            "total_tokens": self._total_tokens,
            "total_cost": self._total_cost,
            "cache_size": len(self._cache),
        }
    
    def validate_messages(self, messages: List[LLMMessage]) -> None:
        """
        Validate messages before sending.
        
        Args:
            messages: List of messages to validate
        """
        if not messages:
            raise LLMError(
                message="No messages provided",
                provider=self.provider_name,
                error_type="validation",
                retryable=False,
            )
        
        for msg in messages:
            if not msg.content:
                raise LLMError(
                    message=f"Empty content for {msg.role} message",
                    provider=self.provider_name,
                    error_type="validation",
                    retryable=False,
                )
            
            if msg.role not in ["system", "user", "assistant"]:
                raise LLMError(
                    message=f"Invalid role: {msg.role}",
                    provider=self.provider_name,
                    error_type="validation",
                    retryable=False,
                )