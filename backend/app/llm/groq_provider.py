"""
HealthConnect AI - Groq Provider
=================================
Groq Cloud API integration (OpenAI-compatible).
Free tier with generous rate limits.
"""

import time
import json
from typing import List, AsyncGenerator, Optional
import aiohttp

from app.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq Cloud LLM provider."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.model = config.model
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate text using Groq API."""
        start_time = time.time()
        
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        payload = {
            "model": self.model,
            "messages": openai_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:
                    
                    if response.status == 401:
                        raise LLMError(
                            message="Invalid Groq API key",
                            provider=self.provider_name,
                            error_type="authentication",
                            retryable=False,
                        )
                    
                    if response.status == 429:
                        raise LLMError(
                            message="Rate limit exceeded. Wait a minute and try again.",
                            provider=self.provider_name,
                            error_type="rate_limit",
                            retryable=True,
                        )
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMError(
                            message=f"Groq API error ({response.status}): {error_text[:200]}",
                            provider=self.provider_name,
                            error_type="api_error",
                            retryable=True,
                        )
                    
                    result = await response.json()
            
            generated_text = ""
            if "choices" in result and result["choices"]:
                generated_text = result["choices"][0].get("message", {}).get("content", "")
            
            latency_ms = (time.time() - start_time) * 1000
            total_tokens = result.get("usage", {}).get("total_tokens", self.count_tokens(generated_text))
            
            return LLMResponse(
                text=generated_text.strip(),
                provider=self.provider_name,
                model=self.model,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                finish_reason="stop",
            )
            
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(
                message=f"Connection error: {str(e)}",
                provider=self.provider_name,
                error_type="connection",
                retryable=True,
            )
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream text generation from Groq."""
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        payload = {
            "model": self.model,
            "messages": openai_messages,
            "stream": True,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith("data: "):
                            data = line_text[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if delta.get("content"):
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Approximate token count."""
        return len(text) // 4
