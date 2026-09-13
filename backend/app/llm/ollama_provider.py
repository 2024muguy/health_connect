"""
HealthConnect AI - Ollama Provider
===================================
Local Ollama LLM integration with streaming support.
"""

import time
import json
from typing import List, Dict, Any, AsyncGenerator, Optional
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


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = (config.api_key or "http://localhost:11434").rstrip('/')
        self.generate_url = f"{self.base_url}/api/generate"
        self.embeddings_url = f"{self.base_url}/api/embeddings"
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate text using Ollama."""
        start_time = time.time()
        prompt = self._build_prompt(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
                "num_thread": 4,  # Use 4 CPU threads
            },
        }
        
        try:
            # Use streaming internally for better response
            full_response = ""
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.generate_url,
                    json={**payload, "stream": True},
                    timeout=aiohttp.ClientTimeout(total=300),  # 5 minutes
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMError(
                            message=f"Ollama error ({response.status}): {error_text[:200]}",
                            provider=self.provider_name,
                            error_type="api_error",
                            retryable=False,
                        )
                    
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text:
                            try:
                                chunk = json.loads(line_text)
                                token = chunk.get("response", "")
                                if token:
                                    full_response += token
                                if chunk.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                text=full_response.strip(),
                provider=self.provider_name,
                model=self.model,
                total_tokens=self.count_tokens(full_response),
                latency_ms=latency_ms,
                finish_reason="stop",
            )
            
        except asyncio.TimeoutError:
            raise LLMError(
                message="Ollama timed out. Model is too slow on this hardware.",
                provider=self.provider_name,
                error_type="timeout",
                retryable=True,
            )
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(
                message=f"Ollama error: {str(e)}",
                provider=self.provider_name,
                error_type="unknown",
                retryable=True,
            )
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream text generation from Ollama."""
        prompt = self._build_prompt(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": self.config.temperature},
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.generate_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300),
                ) as response:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text:
                            try:
                                chunk = json.loads(line_text)
                                if chunk.get("response"):
                                    yield chunk["response"]
                                if chunk.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Approximate token count."""
        return len(text) // 4
    
    def _build_prompt(self, messages: List[LLMMessage]) -> str:
        """Build prompt from messages."""
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"### System:\n{msg.content}\n")
            elif msg.role == "user":
                parts.append(f"### User:\n{msg.content}\n")
            else:
                parts.append(f"### Assistant:\n{msg.content}\n")
        parts.append("### Assistant:\n")
        return "\n".join(parts)
    
    async def check_availability(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    return response.status == 200
        except:
            return False
