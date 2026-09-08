"""
HealthConnect AI - Local Provider
==================================
Local LLM provider for offline fallback.

Features:
- Uses local models (if available)
- Basic response generation
- No API key required
"""

import time
from typing import List, Dict, Any, AsyncGenerator, Optional

from app.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


class LocalProvider(BaseLLMProvider):
    """
    Local LLM provider for offline fallback.
    Uses transformers library if available.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._model = None
        self._tokenizer = None
        self._try_load_model()
    
    def _try_load_model(self) -> None:
        """Try to load local model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            model_name = self.config.model or "microsoft/DialoGPT-small"
            
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModelForCausalLM.from_pretrained(model_name)
            
            logger.info(f"Loaded local model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to load local model: {e}")
            self._model = None
            self._tokenizer = None
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text using local model.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse: Response
        """
        if not self._model or not self._tokenizer:
            raise LLMError(
                message="Local model not available",
                provider=self.provider_name,
                error_type="model_not_available",
                retryable=False,
            )
        
        start_time = time.time()
        
        try:
            # Build prompt from messages
            prompt = ""
            for msg in messages:
                if msg.role == "system":
                    prompt += f"[System]: {msg.content}\n"
                elif msg.role == "user":
                    prompt += f"[User]: {msg.content}\n"
                else:
                    prompt += f"[Assistant]: {msg.content}\n"
            
            inputs = self._tokenizer.encode(prompt, return_tensors="pt")
            
            outputs = self._model.generate(
                inputs,
                max_new_tokens=kwargs.get("max_tokens", 100),
                temperature=kwargs.get("temperature", 0.7),
                do_sample=True,
                pad_token_id=self._tokenizer.eos_token_id,
            )
            
            response_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from response
            if prompt in response_text:
                response_text = response_text.replace(prompt, "").strip()
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                text=response_text,
                provider=self.provider_name,
                model=self.config.model,
                prompt_tokens=len(inputs[0]),
                completion_tokens=self.count_tokens(response_text),
                total_tokens=len(inputs[0]) + self.count_tokens(response_text),
                latency_ms=latency_ms,
                finish_reason="stop",
            )
            
        except Exception as e:
            raise LLMError(
                message=f"Local generation error: {str(e)}",
                provider=self.provider_name,
                error_type="generation_error",
                retryable=False,
            )
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Stream text generation from local model.
        Note: Local models don't support true streaming, so we yield all at once.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Yields:
            str: Text chunks
        """
        response = await self.generate(messages, **kwargs)
        yield response.text
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using local tokenizer if available"""
        if self._tokenizer:
            return len(self._tokenizer.encode(text))
        return len(text) // 4