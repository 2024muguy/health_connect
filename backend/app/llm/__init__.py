"""
HealthConnect AI - LLM Package
===============================
LLM providers: Ollama (local) and HuggingFace (cloud)
"""

from app.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)

__all__ = [
    "BaseLLMProvider",
    "LLMConfig",
    "LLMMessage",
    "LLMResponse",
    "LLMError",
]
