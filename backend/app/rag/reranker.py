"""
HealthConnect AI - Cross-Encoder Reranker
==========================================
Re-ranking retrieved chunks for better precision.

Features:
- Cross-encoder re-ranking
- Score normalization
- Diversity-aware selection
- Batch re-ranking
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.rag.retriever import RetrievalResult

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CrossEncoderReranker:
    """
    Cross-encoder reranker for improving retrieval precision.
    Uses a cross-encoder model to score query-document pairs.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.rag.RERANKER_MODEL
        self._model = None
        self._loaded = False
        logger.info(f"CrossEncoderReranker initialized with {self.model_name}")
    
    def _load_model(self) -> None:
        """Load cross-encoder model"""
        if self._loaded:
            return
        
        try:
            from sentence_transformers import CrossEncoder
            
            self._model = CrossEncoder(self.model_name)
            self._loaded = True
            logger.info(f"Loaded cross-encoder model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to load cross-encoder: {e}")
            self._model = None
            self._loaded = False
    
    async def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int = 5,
        diversity_weight: float = 0.1,
    ) -> List[RetrievalResult]:
        """
        Re-rank retrieval results.
        
        Args:
            query: Query text
            results: Initial retrieval results
            top_k: Number of results to return
            diversity_weight: Weight for diversity in selection
            
        Returns:
            List[RetrievalResult]: Re-ranked results
        """
        if not results:
            return []
        
        # If model not available, return original results
        self._load_model()
        if not self._model:
            logger.warning("Cross-encoder not available, returning original order")
            return results[:top_k]
        
        # Score all query-document pairs
        pairs = [(query, result.text) for result in results]
        
        try:
            scores = await asyncio.to_thread(
                self._model.predict,
                pairs,
            )
        except Exception as e:
            logger.error(f"Cross-encoder scoring failed: {e}")
            return results[:top_k]
        
        # Normalize scores to 0-1
        if len(scores) > 1:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                scores = [(s - min_score) / (max_score - min_score) for s in scores]
            else:
                scores = [1.0] * len(scores)
        else:
            scores = [1.0]
        
        # Update scores
        for result, score in zip(results, scores):
            result.score = float(score)
            result.retrieval_method = "cross_encoder"
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Apply diversity-aware selection
        if diversity_weight > 0:
            results = self._diversity_selection(results, top_k, diversity_weight)
        
        return results[:top_k]
    
    def _diversity_selection(
        self,
        results: List[RetrievalResult],
        top_k: int,
        diversity_weight: float,
    ) -> List[RetrievalResult]:
        """
        Select results with diversity consideration.
        Avoids selecting very similar chunks.
        
        Args:
            results: Sorted results
            top_k: Number to select
            diversity_weight: Weight for diversity
            
        Returns:
            List[RetrievalResult]: Selected results
        """
        if len(results) <= top_k:
            return results
        
        selected = [results[0]]
        remaining = results[1:]
        
        while len(selected) < top_k and remaining:
            best_score = -float('inf')
            best_idx = 0
            
            for i, candidate in enumerate(remaining):
                # Calculate similarity to already selected
                max_similarity = 0
                for sel in selected:
                    similarity = self._text_similarity(candidate.text, sel.text)
                    max_similarity = max(max_similarity, similarity)
                
                # Combine relevance score with diversity
                combined_score = (
                    candidate.score -
                    diversity_weight * max_similarity
                )
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_idx = i
            
            selected.append(remaining.pop(best_idx))
        
        return selected
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using Jaccard"""
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)
    
    async def rerank_batch(
        self,
        queries: List[str],
        results_list: List[List[RetrievalResult]],
        top_k: int = 5,
    ) -> List[List[RetrievalResult]]:
        """
        Re-rank multiple query-result pairs.
        
        Args:
            queries: List of queries
            results_list: List of result lists
            top_k: Number of results
            
        Returns:
            List[List[RetrievalResult]]: Re-ranked results
        """
        return [
            await self.rerank(query, results, top_k)
            for query, results in zip(queries, results_list)
        ]