"""
HealthConnect AI - LLM Base Classes
=====================================
Base classes and types for all LLM providers.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, AsyncGenerator
from abc import ABC, abstractmethod


@dataclass
class LLMMessage:
    """Represents a chat message."""
    role: str  # "system", "user", "assistant"
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""
    provider: str = ""  # Provider name (e.g., "ollama", "huggingface")
    api_key: str = ""
    model: str = ""
    max_tokens: int = 512
    temperature: float = 0.3
    timeout: int = 60


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    text: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0
    finish_reason: str = "stop"


class LLMError(Exception):
    """Base exception for LLM provider errors."""
    
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        error_type: str = "unknown",
        retryable: bool = False,
    ):
        self.message = message
        self.provider = provider
        self.error_type = error_type
        self.retryable = retryable
        super().__init__(self.message)


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_key = config.api_key
        self.model = config.model
        self.provider_name = config.provider or self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream a response from the LLM."""
        pass
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (approximate)."""
        return len(text) // 4
