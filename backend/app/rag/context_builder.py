"""
HealthConnect AI - Context Builder
===================================
Builds context from retrieved chunks for LLM generation.

Features:
- Context assembly
- Token limit management
- Context truncation
- Source tracking
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.rag.retriever import RetrievalResult

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class BuiltContext:
    """Built context for LLM"""
    context_text: str
    sources: List[Dict[str, Any]]
    total_tokens: int
    chunks_used: int
    truncated: bool


class ContextBuilder:
    """
    Context builder for assembling retrieved chunks.
    Ensures context fits within LLM token limits.
    """
    
    def __init__(self, max_tokens: Optional[int] = None):
        self.max_tokens = max_tokens or settings.rag.MAX_CONTEXT_LENGTH
        self.token_estimate_chars = 4  # Approximate chars per token
    
    def build_context(
        self,
        results: List[RetrievalResult],
        max_tokens: Optional[int] = None,
        include_citations: bool = True,
    ) -> BuiltContext:
        """
        Build context from retrieval results.
        
        Args:
            results: Retrieved results
            max_tokens: Maximum context tokens
            include_citations: Whether to include citations
            
        Returns:
            BuiltContext: Built context
        """
        max_tokens = max_tokens or self.max_tokens
        max_chars = max_tokens * self.token_estimate_chars
        
        context_parts = []
        sources = []
        total_chars = 0
        chunks_used = 0
        truncated = False
        
        for i, result in enumerate(results, 1):
            # Format chunk with citation
            if include_citations:
                chunk_text = (
                    f"[Source {i}] (Chunk: {result.chunk_id})\n"
                    f"{result.text}\n"
                )
            else:
                chunk_text = result.text + "\n"
            
            chunk_chars = len(chunk_text)
            
            # Check if adding this chunk exceeds limit
            if total_chars + chunk_chars > max_chars:
                if chunks_used == 0:
                    # Must include at least one chunk
                    truncated_chunk = self._truncate_chunk(
                        chunk_text,
                        max_chars - total_chars,
                    )
                    context_parts.append(truncated_chunk)
                    sources.append(self._extract_source(result, i))
                    chunks_used += 1
                    truncated = True
                else:
                    truncated = True
                break
            
            context_parts.append(chunk_text)
            sources.append(self._extract_source(result, i))
            total_chars += chunk_chars
            chunks_used += 1
        
        context_text = "\n".join(context_parts)
        total_tokens = total_chars // self.token_estimate_chars
        
        logger.info(
            f"Built context: {chunks_used} chunks, "
            f"{total_tokens} tokens, truncated={truncated}"
        )
        
        return BuiltContext(
            context_text=context_text,
            sources=sources,
            total_tokens=total_tokens,
            chunks_used=chunks_used,
            truncated=truncated,
        )
    
    def _extract_source(
        self,
        result: RetrievalResult,
        index: int,
    ) -> Dict[str, Any]:
        """Extract source information from result"""
        return {
            "index": index,
            "chunk_id": result.chunk_id,
            "document_id": result.metadata.get("document_id", ""),
            "section": result.metadata.get("section", ""),
            "title": result.metadata.get("title", ""),
            "score": result.score,
            "retrieval_method": result.retrieval_method,
        }
    
    def _truncate_chunk(self, text: str, max_chars: int) -> str:
        """Truncate chunk to fit within limit"""
        if len(text) <= max_chars:
            return text
        
        return text[:max_chars] + "...\n"
    
    def build_context_from_chunks(
        self,
        chunks: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Build context from raw chunk dictionaries.
        
        Args:
            chunks: List of chunk dictionaries
            max_tokens: Maximum context tokens
            
        Returns:
            str: Context text
        """
        max_tokens = max_tokens or self.max_tokens
        max_chars = max_tokens * self.token_estimate_chars
        
        context_parts = []
        total_chars = 0
        
        for chunk in chunks:
            chunk_text = chunk.get("text", "")
            chunk_chars = len(chunk_text)
            
            if total_chars + chunk_chars > max_chars:
                break
            
            context_parts.append(chunk_text)
            total_chars += chunk_chars
        
        return "\n\n".join(context_parts)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text) // self.token_estimate_chars
    
    def merge_contexts(
        self,
        contexts: List[BuiltContext],
    ) -> BuiltContext:
        """
        Merge multiple built contexts.
        
        Args:
            contexts: List of BuiltContext
            
        Returns:
            BuiltContext: Merged context
        """
        merged_text = "\n\n".join(c.context_text for c in contexts)
        merged_sources = []
        for c in contexts:
            merged_sources.extend(c.sources)
        
        return BuiltContext(
            context_text=merged_text,
            sources=merged_sources,
            total_tokens=sum(c.total_tokens for c in contexts),
            chunks_used=sum(c.chunks_used for c in contexts),
            truncated=any(c.truncated for c in contexts),
        )