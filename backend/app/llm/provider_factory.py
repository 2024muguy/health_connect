"""
HealthConnect AI - LLM Provider Factory
========================================
Factory for creating and managing LLM providers.
Priority: Groq (cloud) > Ollama (local fallback)
"""

from typing import Dict, Optional, List
from app.llm.base import BaseLLMProvider, LLMConfig
from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class LLMProviderFactory:
    """Factory for LLM providers."""
    
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
    
    async def initialize(self):
        """Initialize available providers."""
        
        # 1. Groq (cloud - primary, fast, free tier)
        if settings.groq.API_KEY:
            try:
                from app.llm.groq_provider import GroqProvider
                config = LLMConfig(
                    provider="groq",
                    api_key=settings.groq.API_KEY,
                    model=settings.groq.MODEL,
                    max_tokens=settings.groq.MAX_TOKENS,
                    temperature=settings.groq.TEMPERATURE,
                    timeout=60,
                )
                self._providers["groq"] = GroqProvider(config)
                logger.info("✅ Groq provider initialized (cloud)")
            except Exception as e:
                logger.warning(f"Groq initialization error: {e}")
        
        # 2. Ollama (local - fallback)
        try:
            from app.llm.ollama_provider import OllamaProvider
            config = LLMConfig(
                provider="ollama",
                api_key=settings.ollama.BASE_URL,
                model=settings.ollama.MODEL,
                max_tokens=512,
                temperature=0.3,
                timeout=300,
            )
            ollama_provider = OllamaProvider(config)
            if await ollama_provider.check_availability():
                self._providers["ollama"] = ollama_provider
                logger.info("✅ Ollama provider initialized (local fallback)")
            else:
                logger.info("Ollama not running - skipping")
        except Exception as e:
            logger.warning(f"Ollama initialization error: {e}")
        
        if not self._providers:
            logger.warning("No LLM providers available!")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self._providers.keys())
    
    def get_provider(self, name: str) -> BaseLLMProvider:
        """Get a provider by name."""
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not available")
        return self._providers[name]
    
    @property
    def default_provider(self) -> Optional[BaseLLMProvider]:
        """Get the default provider (Groq preferred, Ollama fallback)."""
        if "groq" in self._providers:
            return self._providers["groq"]
        if "ollama" in self._providers:
            return self._providers["ollama"]
        return None


async def get_llm_provider(name: Optional[str] = None) -> BaseLLMProvider:
    """Get an LLM provider by name or default."""
    factory = LLMProviderFactory()
    await factory.initialize()
    
    if name:
        return factory.get_provider(name)
    return factory.default_provider
