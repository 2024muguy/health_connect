"""
HealthConnect AI - Hybrid Retriever
====================================
Advanced retrieval strategies for RAG pipeline.

Features:
- Vector search (semantic similarity)
- Keyword search (BM25)
- Hybrid search (RRF fusion)
- Query expansion
- Filtered search
"""

import asyncio
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
import math

from app.rag.embedding import EmbeddingGenerator
from app.rag.vector_store import VectorStoreManager

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class RetrievalResult:
    """Retrieval result"""
    chunk_id: str
    text: str
    score: float
    retrieval_method: str
    rank: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "score": self.score,
            "retrieval_method": self.retrieval_method,
            "rank": self.rank,
            "metadata": self.metadata,
        }


class HybridRetriever:
    """
    Hybrid retriever combining multiple retrieval strategies.
    
    Strategies:
    1. Vector search (semantic similarity)
    2. Keyword search (BM25)
    3. Hybrid fusion (Reciprocal Rank Fusion)
    """
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStoreManager()
        self.rrf_constant = settings.rag.RRF_CONSTANT
        self.hybrid_alpha = settings.rag.HYBRID_SEARCH_ALPHA
        self._keyword_index: Dict[str, Dict[str, int]] = {}
        self._document_frequency: Counter = Counter()
        self._total_documents = 0
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        retrieval_method: str = "hybrid",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks for query.
        
        Args:
            query: Query text
            top_k: Number of results
            retrieval_method: "vector", "keyword", or "hybrid"
            filters: Metadata filters
            
        Returns:
            List[RetrievalResult]: Retrieved results
        """
        logger.info(f"Retrieving for query: '{query[:50]}...' (method: {retrieval_method})")
        
        if retrieval_method == "vector":
            return await self._vector_search(query, top_k, filters)
        elif retrieval_method == "keyword":
            return await self._keyword_search(query, top_k)
        elif retrieval_method == "hybrid":
            return await self._hybrid_search(query, top_k, filters)
        else:
            raise ValueError(f"Unknown retrieval method: {retrieval_method}")
    
    async def _vector_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[RetrievalResult]:
        """
        Vector similarity search.
        
        Args:
            query: Query text
            top_k: Number of results
            filters: Metadata filters
            
        Returns:
            List[RetrievalResult]: Results
        """
        # Generate query embedding
        query_embedding = await self.embedding_generator.embed_query(query)
        
        # Search vector store
        results = await self.vector_store.search(
            query_embedding,
            top_k=top_k * 2,  # Get extra for re-ranking
            filters=filters,
        )
        
        retrieval_results = []
        for chunk_id, score, metadata in results:
            retrieval_results.append(RetrievalResult(
                chunk_id=chunk_id,
                text=metadata.get("text", ""),
                score=score,
                retrieval_method="vector",
                metadata=metadata,
            ))
        
        return retrieval_results[:top_k]
    
    async def _keyword_search(
        self,
        query: str,
        top_k: int,
    ) -> List[RetrievalResult]:
        """
        Keyword search using BM25.
        
        Args:
            query: Query text
            top_k: Number of results
            
        Returns:
            List[RetrievalResult]: Results
        """
        # Tokenize query
        query_terms = self._tokenize_query(query)
        
        if not query_terms:
            return []
        
        # BM25 scoring
        scores = {}
        k1 = 1.5
        b = 0.75
        
        for term in query_terms:
            if term not in self._document_frequency:
                continue
            
            df = self._document_frequency[term]
            idf = math.log((self._total_documents - df + 0.5) / (df + 0.5) + 1)
            
            if term in self._keyword_index:
                for doc_id, tf in self._keyword_index[term].items():
                    doc_length = self._get_doc_length(doc_id)
                    avg_doc_length = self._get_avg_doc_length()
                    
                    bm25_score = idf * (
                        (tf * (k1 + 1)) /
                        (tf + k1 * (1 - b + b * doc_length / avg_doc_length))
                    )
                    
                    scores[doc_id] = scores.get(doc_id, 0) + bm25_score
        
        # Sort by score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            chunk = self.vector_store._chunk_map.get(doc_id)
            if chunk:
                results.append(RetrievalResult(
                    chunk_id=doc_id,
                    text=chunk.text,
                    score=score,
                    retrieval_method="keyword",
                ))
        
        return results
    
    async def _hybrid_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[RetrievalResult]:
        """
        Hybrid search combining vector and keyword results.
        Uses Reciprocal Rank Fusion (RRF).
        
        Args:
            query: Query text
            top_k: Number of results
            filters: Metadata filters
            
        Returns:
            List[RetrievalResult]: Fused results
        """
        # Get vector results
        vector_results = await self._vector_search(query, top_k * 2, filters)
        
        # Get keyword results
        keyword_results = await self._keyword_search(query, top_k * 2)
        
        # Reciprocal Rank Fusion
        rrf_scores = {}
        result_map = {}
        
        # Add vector results
        for rank, result in enumerate(vector_results, 1):
            rrf_scores[result.chunk_id] = rrf_scores.get(result.chunk_id, 0) + (
                self.hybrid_alpha / (self.rrf_constant + rank)
            )
            result_map[result.chunk_id] = result
        
        # Add keyword results
        for rank, result in enumerate(keyword_results, 1):
            rrf_scores[result.chunk_id] = rrf_scores.get(result.chunk_id, 0) + (
                (1 - self.hybrid_alpha) / (self.rrf_constant + rank)
            )
            if result.chunk_id not in result_map:
                result_map[result.chunk_id] = result
        
        # Sort by RRF score
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build final results
        final_results = []
        for chunk_id, rrf_score in sorted_results[:top_k]:
            result = result_map[chunk_id]
            result.score = rrf_score
            result.retrieval_method = "hybrid"
            final_results.append(result)
        
        return final_results
    
    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize query for keyword search"""
        # Simple whitespace tokenization with lowercasing
        tokens = re.findall(r'\w+', query.lower())
        
        # Remove stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
            'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'can', 'could', 'should',
            'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
        }
        
        return [t for t in tokens if t not in stopwords and len(t) > 2]
    
    def _get_doc_length(self, doc_id: str) -> int:
        """Get document length for BM25"""
        chunk = self.vector_store._chunk_map.get(doc_id)
        if chunk:
            return len(chunk.text.split())
        return 0
    
    def _get_avg_doc_length(self) -> float:
        """Get average document length"""
        if self._total_documents == 0:
            return 1.0
        
        chunks = self.vector_store._chunk_map.values()
        if not chunks:
            return 1.0
        
        total_length = sum(len(c.text.split()) for c in chunks)
        return total_length / len(chunks)
    
    def build_keyword_index(self, chunks: List[Any]) -> None:
        """
        Build keyword index for BM25 search.
        
        Args:
            chunks: List of chunks
        """
        self._keyword_index = {}
        self._document_frequency = Counter()
        self._total_documents = len(chunks)
        
        for chunk in chunks:
            terms = self._tokenize_query(chunk.text)
            term_counts = Counter(terms)
            
            for term, count in term_counts.items():
                if term not in self._keyword_index:
                    self._keyword_index[term] = {}
                self._keyword_index[term][chunk.chunk_id] = count
                self._document_frequency[term] += 1
        
        logger.info(f"Built keyword index with {len(self._keyword_index)} terms")
    
    async def retrieve_with_context(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
        top_k: int = 5,
    ) -> List[RetrievalResult]:
        """
        Retrieve with conversation context.
        Expands query using conversation history.
        
        Args:
            query: Current query
            conversation_history: Previous messages
            top_k: Number of results
            
        Returns:
            List[RetrievalResult]: Results
        """
        # Build contextual query
        contextual_query = query
        
        if conversation_history:
            # Extract key terms from history
            history_terms = self._extract_history_terms(conversation_history)
            if history_terms:
                contextual_query = f"{query} {' '.join(history_terms[:5])}"
        
        return await self.retrieve(contextual_query, top_k=top_k)
    
    def _extract_history_terms(self, history: List[Dict[str, str]]) -> List[str]:
        """Extract key terms from conversation history"""
        all_terms = []
        
        for message in history:
            content = message.get("content", "")
            terms = self._tokenize_query(content)
            all_terms.extend(terms)
        
        # Return most common terms
        term_counts = Counter(all_terms)
        return [term for term, _ in term_counts.most_common(10)]