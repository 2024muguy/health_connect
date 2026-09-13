"""
HealthConnect AI - Knowledge Agent (Production Ready)
======================================================
Retrieves knowledge from RAG pipeline.
Handles empty results gracefully without loading reranker.
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

from config.logging_config import get_logger

logger = get_logger(__name__)


class KnowledgeAgent(BaseAgent):
    """Knowledge retrieval agent."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.KNOWLEDGE, config)
        self.retriever = HybridRetriever()
        logger.info("KnowledgeAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Retrieve knowledge for query."""
        start_time = time.time()
        
        # Retrieve chunks
        results = await self.retriever.retrieve(
            query=context.query,
            top_k=5,
            retrieval_method="hybrid",
        )
        
        # If no results, return immediately
        if not results:
            logger.info("No knowledge retrieved")
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output={
                    "chunks": [],
                    "sources": [],
                },
                confidence=0.0,
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        
        # Build chunks and sources
        chunks = []
        sources = []
        
        for result in results:
            chunks.append({
                "chunk_id": result.chunk_id,
                "text": result.text,
                "score": result.score,
                "retrieval_method": result.retrieval_method,
                "metadata": result.metadata,
            })
            
            if result.metadata.get("document_id"):
                sources.append({
                    "document_id": result.metadata["document_id"],
                    "chunk_id": result.chunk_id,
                    "score": result.score,
                })
        
        execution_time = (time.time() - start_time) * 1000
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "chunks": chunks,
                "sources": sources,
            },
            confidence=0.7 if results else 0.0,
            execution_time_ms=execution_time,
        )
