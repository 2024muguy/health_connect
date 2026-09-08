"""
HealthConnect AI - Google Gemini Provider
==========================================
Google Gemini integration.

Features:
- Gemini Pro
- Streaming
- Token counting
- Error handling
"""

import time
from typing import List, Dict, Any, AsyncGenerator, Optional
import google.generativeai as genai

from app.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini provider implementation.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model_instance = genai.GenerativeModel(config.model)
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text using Gemini API.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse: Response
        """
        start_time = time.time()
        
        try:
            # Convert messages to Gemini format
            prompt_parts = []
            system_instruction = ""
            
            for msg in messages:
                if msg.role == "system":
                    system_instruction = msg.content
                else:
                    prompt_parts.append(f"{msg.role.upper()}: {msg.content}")
            
            prompt = "\n".join(prompt_parts)
            
            response = await self.model_instance.generate_content_async(
                prompt,
                generation_config={
                    "max_output_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature),
                },
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            text = response.text if response.text else ""
            
            return LLMResponse(
                text=text,
                provider=self.provider_name,
                model=self.config.model,
                prompt_tokens=self.count_tokens(prompt),
                completion_tokens=self.count_tokens(text),
                total_tokens=self.count_tokens(prompt + text),
                latency_ms=latency_ms,
                finish_reason="stop",
                raw_response=response,
            )
            
        except Exception as e:
            raise LLMError(
                message=f"Gemini error: {str(e)}",
                provider=self.provider_name,
                error_type="api_error",
                retryable=True,
            )
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Stream text generation from Gemini.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Yields:
            str: Text chunks
        """
        try:
            prompt_parts = []
            for msg in messages:
                if msg.role != "system":
                    prompt_parts.append(f"{msg.role.upper()}: {msg.content}")
            
            prompt = "\n".join(prompt_parts)
            
            response = await self.model_instance.generate_content_async(
                prompt,
                generation_config={
                    "max_output_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature),
                },
                stream=True,
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise LLMError(
                message=f"Streaming error: {str(e)}",
                provider=self.provider_name,
                error_type="stream_error",
                retryable=True,
            )
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens for Gemini.
        
        Args:
            text: Text to count
            
        Returns:
            int: Token count
        """
        try:
            result = self.model_instance.count_tokens(text)
            return result.total_tokens
        except Exception:
            return len(text) // 4