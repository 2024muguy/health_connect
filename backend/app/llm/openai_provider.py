"""
HealthConnect AI - OpenAI Provider
===================================
OpenAI GPT-4, GPT-3.5 integration.

Features:
- Chat completion
- Streaming
- Token counting
- Embedding generation
- Error handling
"""

import asyncio
import time
from typing import List, Dict, Any, AsyncGenerator, Optional
import openai
from openai import AsyncOpenAI

from app.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMError,
)
from config.logging_config import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider implementation.
    Supports GPT-4, GPT-3.5-turbo, and embedding models.
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            timeout=config.timeout,
            max_retries=0,  # We handle retries ourselves
        )
        self._embedding_cache = {}
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs,
    ) -> LLMResponse:
        """
        Generate text using OpenAI API.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse: Response
        """
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[msg.to_dict() for msg in messages],
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                top_p=kwargs.get("top_p", self.config.top_p),
                frequency_penalty=kwargs.get("frequency_penalty", self.config.frequency_penalty),
                presence_penalty=kwargs.get("presence_penalty", self.config.presence_penalty),
                stop=kwargs.get("stop", self.config.stop_sequences or None),
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                text=response.choices[0].message.content,
                provider=self.provider_name,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response,
                request_id=response.id,
            )
            
        except openai.RateLimitError as e:
            raise LLMError(
                message=f"Rate limit exceeded: {str(e)}",
                provider=self.provider_name,
                error_type="rate_limit",
                retryable=True,
            )
        except openai.APIError as e:
            raise LLMError(
                message=f"API error: {str(e)}",
                provider=self.provider_name,
                error_type="api_error",
                retryable=True,
            )
        except openai.AuthenticationError as e:
            raise LLMError(
                message=f"Authentication failed: {str(e)}",
                provider=self.provider_name,
                error_type="authentication",
                retryable=False,
            )
        except openai.APITimeoutError as e:
            raise LLMError(
                message=f"Timeout: {str(e)}",
                provider=self.provider_name,
                error_type="timeout",
                retryable=True,
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
        Stream text generation from OpenAI.
        
        Args:
            messages: List of messages
            **kwargs: Additional parameters
            
        Yields:
            str: Text chunks
        """
        try:
            stream = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[msg.to_dict() for msg in messages],
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except openai.RateLimitError as e:
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
        Count tokens using tiktoken.
        
        Args:
            text: Text to count
            
        Returns:
            int: Token count
        """
        try:
            import tiktoken
            
            # Use cl100k_base for GPT-4 and GPT-3.5-turbo
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: approximate token count (4 chars per token)
            return len(text) // 4
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            return len(text) // 4
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small",
    ) -> List[float]:
        """
        Generate embedding using OpenAI.
        
        Args:
            text: Text to embed
            model: Embedding model name
            
        Returns:
            List[float]: Embedding vector
        """
        # Check cache
        cache_key = f"{model}:{hash(text)}"
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text,
            )
            
            embedding = response.data[0].embedding
            
            # Cache result
            self._embedding_cache[cache_key] = embedding
            if len(self._embedding_cache) > 10000:
                for key in list(self._embedding_cache.keys())[:5000]:
                    del self._embedding_cache[key]
            
            return embedding
            
        except openai.RateLimitError as e:
            raise LLMError(
                message=f"Embedding rate limit: {str(e)}",
                provider=self.provider_name,
                error_type="rate_limit",
                retryable=True,
            )
        except Exception as e:
            raise LLMError(
                message=f"Embedding error: {str(e)}",
                provider=self.provider_name,
                error_type="embedding_error",
                retryable=True,
            )
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small",
        batch_size: int = 32,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts
            model: Embedding model
            batch_size: Batch size
            
        Returns:
            List[List[float]]: List of embeddings
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = await self.client.embeddings.create(
                    model=model,
                    input=batch,
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Cache results
                for text, embedding in zip(batch, batch_embeddings):
                    cache_key = f"{model}:{hash(text)}"
                    self._embedding_cache[cache_key] = embedding
                
            except Exception as e:
                logger.error(f"Batch embedding failed for batch {i // batch_size}: {e}")
                raise LLMError(
                    message=f"Batch embedding error: {str(e)}",
                    provider=self.provider_name,
                    error_type="embedding_error",
                    retryable=True,
                )
        
        return embeddings