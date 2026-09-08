"""
HealthConnect AI - Conversation Agent
======================================
Main conversational agent for response generation.

Features:
- RAG-grounded response generation
- Context-aware responses
- Citation inclusion
- Safety-aware generation
"""

import time
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
from config.prompts.prompt_templates import RAGPromptTemplate

logger = get_logger(__name__)


class ConversationAgent(BaseAgent):
    """
    Conversation Agent.
    Generates grounded responses using RAG context.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.CONVERSATION, config)
        self.context_builder = ContextBuilder()
        self.citation_generator = CitationGenerator()
        self.max_history_messages = 10
        
        logger.info("ConversationAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Generate response using RAG.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Generated response
        """
        start_time = time.time()
        
        # Build context from retrieved chunks
        built_context = self.context_builder.build_context(
            self._convert_chunks_to_results(context.retrieved_chunks),
            include_citations=True,
        )
        
        # Generate response
        if self.llm_provider:
            response_text = await self._generate_with_llm(context, built_context)
        else:
            response_text = self._generate_fallback(context, built_context)
        
        # Generate citations
        citations = self.citation_generator.generate_citations(built_context.sources)
        
        # Add citations to response if not already present
        if citations and "[Source" not in response_text:
            response_text += self.citation_generator.generate_reference_list(
                built_context.sources
            )
        
        execution_time = (time.time() - start_time) * 1000
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "response": response_text,
                "citations": citations,
                "context_used": built_context.context_text,
                "sources": built_context.sources,
                "truncated": built_context.truncated,
            },
            confidence=self._calculate_confidence(built_context),
            execution_time_ms=execution_time,
        )
    
    async def _generate_with_llm(
        self,
        context: AgentContext,
        built_context: Any,
    ) -> str:
        """
        Generate response using LLM.
        
        Args:
            context: Agent context
            built_context: Built context
            
        Returns:
            str: Generated response
        """
        from app.llm.base import LLMMessage
        
        # Build messages
        messages = [
            LLMMessage(role="system", content=CONVERSATION_AGENT_PROMPT),
        ]
        
        # Add conversation history
        for msg in context.history[-self.max_history_messages:]:
            messages.append(LLMMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
            ))
        
        # Add current query with context
        user_prompt = RAGPromptTemplate.SYSTEM_PROMPT.format(
            context=built_context.context_text,
            query=context.query,
        )
        messages.append(LLMMessage(role="user", content=user_prompt))
        
        # Generate response
        response = await self.llm_provider.generate_with_retry(
            messages,
            temperature=0.3,
            max_tokens=500,
        )
        
        return response.text
    
    def _generate_fallback(
        self,
        context: AgentContext,
        built_context: Any,
    ) -> str:
        """
        Generate fallback response without LLM.
        
        Args:
            context: Agent context
            built_context: Built context
            
        Returns:
            str: Fallback response
        """
        if built_context.chunks_used > 0:
            # Extract relevant information from context
            return self._extract_answer_from_context(context.query, built_context.context_text)
        
        return (
            "I apologize, but I don't have specific information about that. "
            "Would you like me to help you with appointment scheduling, "
            "clinic information, or other administrative tasks?"
        )
    
    def _extract_answer_from_context(self, query: str, context: str) -> str:
        """
        Extract answer from context using simple heuristics.
        
        Args:
            query: User query
            context: Context text
            
        Returns:
            str: Extracted answer
        """
        # Split context into sentences
        sentences = context.split('\n')
        
        # Find most relevant sentences
        query_terms = set(query.lower().split())
        
        scored_sentences = []
        for sentence in sentences:
            sentence_terms = set(sentence.lower().split())
            overlap = query_terms.intersection(sentence_terms)
            score = len(overlap)
            
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Sort by score
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        # Return top sentences
        if scored_sentences:
            return ' '.join(s for _, s in scored_sentences[:3])
        
        return (
            "Based on the information available, I found some relevant details. "
            "Please let me know if you need more specific information."
        )
    
    def _convert_chunks_to_results(self, chunks: List[Dict[str, Any]]) -> List[Any]:
        """Convert chunk dictionaries to retrieval results"""
        from app.rag.retriever import RetrievalResult
        
        results = []
        for chunk in chunks:
            results.append(RetrievalResult(
                chunk_id=chunk.get("chunk_id", ""),
                text=chunk.get("text", ""),
                score=chunk.get("score", 0.5),
                retrieval_method=chunk.get("retrieval_method", "unknown"),
                metadata=chunk.get("metadata", {}),
            ))
        
        return results
    
    def _calculate_confidence(self, built_context: Any) -> float:
        """Calculate confidence based on context quality"""
        if built_context.chunks_used == 0:
            return 0.1
        
        if built_context.truncated:
            return 0.5
        
        if built_context.chunks_used >= 3:
            return 0.8
        
        return 0.6