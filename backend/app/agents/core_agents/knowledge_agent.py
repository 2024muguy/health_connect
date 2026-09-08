"""
HealthConnect AI - Knowledge Agent
===================================
Retrieves information from the knowledge base.

Features:
- RAG retrieval
- Source tracking
- Relevance scoring
- Information gap detection
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
from app.rag.retriever import HybridRetriever, RetrievalResult
from app.rag.reranker import CrossEncoderReranker

from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class KnowledgeAgent(BaseAgent):
    """
    Knowledge Agent.
    Retrieves relevant information from the knowledge base.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.KNOWLEDGE, config)
        self.retriever = HybridRetriever()
        self.reranker = CrossEncoderReranker()
        self.top_k = settings.rag.TOP_K_RETRIEVAL
        self.min_relevance_score = 0.3
        
        logger.info("KnowledgeAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Retrieve knowledge for query.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Retrieval result
        """
        start_time = time.time()
        
        # Retrieve chunks
        results = await self.retriever.retrieve(
            query=context.query,
            top_k=self.top_k,
            retrieval_method="hybrid",
        )
        
        # Re-rank results
        if results:
            results = await self.reranker.rerank(
                query=context.query,
                results=results,
                top_k=self.top_k,
            )
        
        # Filter by relevance score
        relevant_results = [
            r for r in results
            if r.score >= self.min_relevance_score
        ]
        
        # Convert to output format
        chunks = [r.to_dict() for r in relevant_results]
        sources = [
            {
                "chunk_id": r.chunk_id,
                "score": r.score,
                "retrieval_method": r.retrieval_method,
                "metadata": r.metadata,
            }
            for r in relevant_results
        ]
        
        execution_time = (time.time() - start_time) * 1000
        
        # Check if information was found
        information_found = len(relevant_results) > 0
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "chunks": chunks,
                "sources": sources,
                "information_found": information_found,
                "total_retrieved": len(results),
                "relevant_retrieved": len(relevant_results),
            },
            confidence=self._calculate_retrieval_confidence(relevant_results),
            execution_time_ms=execution_time,
            metadata={
                "information_found": information_found,
                "needs_escalation": not information_found,
            },
        )
    
    def _calculate_retrieval_confidence(
        self,
        results: List[RetrievalResult],
    ) -> float:
        """
        Calculate retrieval confidence.
        
        Args:
            results: Retrieval results
            
        Returns:
            float: Confidence score
        """
        if not results:
            return 0.0
        
        # Average score with count factor
        avg_score = sum(r.score for r in results) / len(results)
        count_factor = min(len(results) / self.top_k, 1.0)
        
        return avg_score * 0.7 + count_factor * 0.3