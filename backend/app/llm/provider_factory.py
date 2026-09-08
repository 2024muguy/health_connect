"""
HealthConnect AI - LLM Provider Factory
========================================
Factory for creating and managing LLM providers.

Features:
- Provider instantiation
- Provider caching
- Automatic provider selection
- Health checks
"""

from typing import Optional, Dict, List, Any

from app.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from app.llm.openai_provider import OpenAIProvider
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.local_provider import LocalProvider

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMProviderFactory:
    """
    Factory for LLM providers.
    Manages provider instances and selection.
    """
    
    _instance = None
    _providers: Dict[str, BaseLLMProvider] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self) -> None:
        """Initialize all configured providers"""
        self._providers = {}
        
        # OpenAI
        if settings.llm.OPENAI_API_KEY:
            config = LLMConfig(
                provider="openai",
                model=settings.llm.OPENAI_MODEL,
                api_key=settings.llm.OPENAI_API_KEY,
                max_tokens=settings.llm.OPENAI_MAX_TOKENS,
                temperature=settings.llm.OPENAI_TEMPERATURE,
            )
            self._providers["openai"] = OpenAIProvider(config)
            logger.info("OpenAI provider initialized")
        
        # Anthropic
        if settings.llm.ANTHROPIC_API_KEY:
            config = LLMConfig(
                provider="anthropic",
                model=settings.llm.ANTHROPIC_MODEL,
                api_key=settings.llm.ANTHROPIC_API_KEY,
                max_tokens=settings.llm.ANTHROPIC_MAX_TOKENS,
                temperature=settings.llm.ANTHROPIC_TEMPERATURE,
            )
            self._providers["anthropic"] = AnthropicProvider(config)
            logger.info("Anthropic provider initialized")
        
        # Google Gemini
        if settings.llm.GOOGLE_API_KEY:
            config = LLMConfig(
                provider="google",
                model=settings.llm.GOOGLE_MODEL,
                api_key=settings.llm.GOOGLE_API_KEY,
                max_tokens=settings.llm.GOOGLE_MAX_TOKENS,
                temperature=settings.llm.GOOGLE_TEMPERATURE,
            )
            self._providers["google"] = GeminiProvider(config)
            logger.info("Google Gemini provider initialized")
        
        # Local fallback
        local_config = LLMConfig(
            provider="local",
            model="microsoft/DialoGPT-small",
            max_tokens=100,
            temperature=0.7,
        )
        self._providers["local"] = LocalProvider(local_config)
        logger.info("Local fallback provider initialized")
    
    async def close(self) -> None:
        """Close all providers"""
        self._providers = {}
        logger.info("LLM providers closed")
    
    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        """
        Get provider by name or default.
        
        Args:
            provider_name: Provider name (openai, anthropic, google, local)
            
        Returns:
            BaseLLMProvider: Provider instance
        """
        if provider_name and provider_name in self._providers:
            return self._providers[provider_name]
        
        # Use default provider
        default = settings.llm.DEFAULT_PROVIDER
        if default in self._providers:
            return self._providers[default]
        
        # Fallback to first available
        for provider in self._providers.values():
            return provider
        
        raise LLMError(
            message="No LLM provider available",
            provider="none",
            error_type="no_provider",
            retryable=False,
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self._providers.keys())
    
    async def get_provider_stats(self) -> Dict[str, Any]:
        """Get stats for all providers"""
        stats = {}
        for name, provider in self._providers.items():
            stats[name] = provider.get_stats()
        return stats


# Singleton instance
_factory = LLMProviderFactory()


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """
    Get LLM provider instance.
    
    Args:
        provider_name: Provider name
        
    Returns:
        BaseLLMProvider: Provider instance
    """
    return _factory.get_provider(provider_name)


async def check_llm_providers() -> bool:
    """Check if any LLM providers are available"""
    return len(_factory.get_available_providers()) > 0