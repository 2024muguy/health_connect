"""
HealthConnect AI - Conversation Agent (Production Ready)
=========================================================
Generates responses using Groq with RAG context.
"""

import time
import os
import requests
from typing import List, Dict, Any, Optional

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)
from app.rag.context_builder import ContextBuilder
from app.rag.citation_generator import CitationGenerator

from config.logging_config import get_logger
from config.prompts.system_prompts import CONVERSATION_AGENT_PROMPT
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)


class ConversationAgent(BaseAgent):
    """Conversation Agent using Groq for response generation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.CONVERSATION, config)
        self.context_builder = ContextBuilder()
        self.citation_generator = CitationGenerator()
        self.max_history_messages = 10
        
        # Groq configuration
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        logger.info(f"ConversationAgent initialized with Groq model: {self.model}")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Generate response using Groq with RAG context."""
        start_time = time.time()
        
        # Build context from retrieved chunks
        built_context = self.context_builder.build_context(
            self._convert_chunks_to_results(context.retrieved_chunks),
            include_citations=True,
        )
        
        logger.info(f"Context: {built_context.chunks_used} chunks, {len(built_context.context_text)} chars")
        
        # Generate response
        response_text = await self._generate_with_groq(context, built_context)
        
        # Generate citations
        citations = self.citation_generator.generate_citations(built_context.sources)
        
        execution_time = (time.time() - start_time) * 1000
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "response": response_text,
                "citations": citations,
                "context_used": built_context.context_text,
                "sources": built_context.sources,
            },
            confidence=0.7 if built_context.chunks_used > 0 else 0.3,
            execution_time_ms=execution_time,
        )
    
    async def _generate_with_groq(self, context: AgentContext, built_context: Any) -> str:
        """Generate response using Groq API directly."""
        if not self.api_key:
            logger.warning("No Groq API key available")
            return self._generate_fallback(context, built_context)
        
        # Build context text (limit to 2000 chars)
        context_text = built_context.context_text[:2000] if built_context.context_text else "No specific context available."
        
        # Build system prompt
        system_prompt = """You are HealthConnect AI Assistant, a professional clinic assistant.
Provide helpful, accurate, and concise answers based on the context provided.
If the answer is not in the context, say you don't have that information.
Never provide medical advice."""
        
        # Build user prompt with context
        user_prompt = f"""Context from Knowledge Base:
{context_text}

User question: {context.query}

Please answer the user's question based on the context above. Be concise and helpful."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 300,
            "temperature": 0.3,
        }
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Run in thread executor to avoid blocking
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content and content.strip():
                    logger.info(f"Groq response generated: {len(content)} chars")
                    return content.strip()
                else:
                    logger.warning("Groq returned empty content")
                    return self._generate_fallback(context, built_context)
            else:
                logger.warning(f"Groq API error: {response.status_code} - {response.text[:200]}")
                return self._generate_fallback(context, built_context)
                
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return self._generate_fallback(context, built_context)
    
    def _generate_fallback(self, context: AgentContext, built_context: Any) -> str:
        """Generate fallback response using context."""
        if built_context.chunks_used > 0:
            # Extract relevant text from context
            return self._extract_answer_from_context(context.query, built_context.context_text)
        
        # No context - generic fallback
        return (
            "I'm here to help with HealthConnect Clinic questions. "
            "You can ask me about appointments, clinic hours, locations, services, and billing. "
            "What would you like to know?"
        )
    
    def _extract_answer_from_context(self, query: str, context: str) -> str:
        """Extract answer from context using text overlap."""
        sentences = context.split('\n')
        query_terms = set(query.lower().split())
        
        scored_sentences = []
        for sentence in sentences:
            sentence_terms = set(sentence.lower().split())
            overlap = query_terms.intersection(sentence_terms)
            if len(overlap) > 0:
                scored_sentences.append((len(overlap), sentence.strip()))
        
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        if scored_sentences:
            # Return top 2-3 sentences
            return ' '.join(s for _, s in scored_sentences[:3])
        
        return "I found some relevant information. Let me know if you need more details."
    
    def _convert_chunks_to_results(self, chunks: List[Dict[str, Any]]) -> List[Any]:
        """Convert chunk dictionaries to retrieval results."""
        from app.rag.retriever import RetrievalResult
        
        results = []
        for chunk in chunks:
            results.append(RetrievalResult(
                chunk_id=chunk.get("chunk_id", ""),
                text=chunk.get("text", ""),
                score=chunk.get("score", 0.5),
                retrieval_method=chunk.get("retrieval_method", "hybrid"),
                metadata=chunk.get("metadata", {}),
            ))
        
        return results
