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


# ============================================
# Query enrichment for retrieval
# ============================================

_ENRICH_RULES = [
    # (trigger words, expansion) — first matching rule wins
    (
        ("saturday", "sunday", "weekend", "morning", "afternoon", "evening",
         "open", "opening", "closed", "closing", "hours", "time"),
        "clinic opening hours schedule days of week Saturday Sunday",
    ),
    (
        ("book", "booking", "appointment", "schedule", "reserve", "slot",
         "visit", "consultation"),
        "how to book an appointment scheduling process",
    ),
    (
        ("service", "services", "offer", "provide", "treat", "treatment",
         "specialty", "specialist", "department"),
        "clinic services offered specialties departments",
    ),
    (
        ("location", "address", "where", "directions", "parking", "clinic"),
        "clinic location address directions",
    ),
    (
        ("insurance", "covered", "coverage", "plan", "provider"),
        "insurance coverage accepted providers",
    ),
    (
        ("cancel", "cancellation", "reschedule", "postpone"),
        "appointment cancellation reschedule policy",
    ),
    (
        ("vaccin", "immuniz", "shot", "flu"),
        "vaccination immunization services",
    ),
    (
        ("lab", "test", "blood", "diagnostic", "imaging", "x-ray", "mri"),
        "laboratory diagnostic services referrals",
    ),
]


def _enrich_retrieval_query(query: str) -> str:
    """
    Expand short/ambiguous queries with domain keywords so the retriever
    finds the right KB chunks. The original query is preserved at the start
    so exact-match intent is not lost.
    """
    if not query:
        return query
    q = query.lower()
    for triggers, expansion in _ENRICH_RULES:
        if any(t in q for t in triggers):
            return f"{query} {expansion}"
    return query


class KnowledgeAgent(BaseAgent):
    """Knowledge retrieval agent."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.KNOWLEDGE, config)
        self.retriever = HybridRetriever()
        logger.info("KnowledgeAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Retrieve knowledge for query."""
        start_time = time.time()
        
        # Enrich ambiguous queries so retrieval finds the right KB chunk
        enriched_query = _enrich_retrieval_query(context.query)
        if enriched_query != context.query:
            logger.info(f"Query enriched: {context.query!r} -> {enriched_query!r}")

        # Retrieve chunks
        results = await self.retriever.retrieve(
            query=enriched_query,
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
