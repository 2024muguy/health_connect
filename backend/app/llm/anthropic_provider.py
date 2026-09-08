"""
HealthConnect AI - Anthropic Provider
======================================
Anthropic Claude integration.

Features:
- Claude 3 Opus, Sonnet, Haiku
- Streaming
- Token counting
- Error handling
"""

import time
from typing import List, Dict, Any, AsyncGenerator, Optional
import anthropic
from anthropic import AsyncAnthropic

from app.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider implementation.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncAnthropic(
            api_key=config.api_key,
            timeout=config.timeout,
        )
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text using Anthropic API.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse: Response
        """
        start_time = time.time()
        
        try:
            # Convert messages to Anthropic format
            system_prompt = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content,
                    })
            
            response = await self.client.messages.create(
                model=kwargs.get("model", self.model),
                system=system_prompt,
                messages=anthropic_messages,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                text=response.content[0].text,
                provider=self.provider_name,
                model=response.model,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                latency_ms=latency_ms,
                finish_reason=response.stop_reason,
                raw_response=response,
                request_id=response.id,
            )
            
        except anthropic.RateLimitError as e:
            raise LLMError(
                message=f"Rate limit exceeded: {str(e)}",
                provider=self.provider_name,
                error_type="rate_limit",
                retryable=True,
            )
        except anthropic.APIError as e:
            raise LLMError(
                message=f"API error: {str(e)}",
                provider=self.provider_name,
                error_type="api_error",
                retryable=True,
            )
        except anthropic.AuthenticationError as e:
            raise LLMError(
                message=f"Authentication failed: {str(e)}",
                provider=self.provider_name,
                error_type="authentication",
                retryable=False,
            )
        except Exception as e:
            raise LLMError(
                message=f"Unexpected error: {str(e)}",
                provider=self.provider_name,
                error_type="unknown",
                retryable=True,
            )
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Stream text generation from Anthropic.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Yields:
            str: Text chunks
        """
        try:
            system_prompt = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content,
                    })
            
            async with self.client.messages.stream(
                model=kwargs.get("model", self.model),
                system=system_prompt,
                messages=anthropic_messages,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except anthropic.RateLimitError as e:
            raise LLMError(
                message=f"Rate limit exceeded: {str(e)}",
                provider=self.provider_name,
                error_type="rate_limit",
                retryable=True,
            )
        except Exception as e:
            raise LLMError(
                message=f"Streaming error: {str(e)}",
                provider=self.provider_name,
                error_type="stream_error",
                retryable=True,
            )
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens for Claude.
        Claude uses approximately 4 characters per token.
        
        Args:
            text: Text to count
            
        Returns:
            int: Token count
        """
        try:
            import anthropic
            return anthropic.count_tokens(text)
        except ImportError:
            return len(text) // 4
        except Exception:
            return len(text) // 4