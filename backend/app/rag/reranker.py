"""
HealthConnect AI - Reranker (Production Ready)
===============================================
Cross-encoder reranking with model caching and empty result handling.
"""

from typing import List, Any, Optional
from config.logging_config import get_logger

logger = get_logger(__name__)


class CrossEncoderReranker:
    """Cross-encoder reranker with lazy model loading."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self._model_loaded = False
        logger.info(f"CrossEncoderReranker initialized with {model_name}")
    
    def _load_model(self):
        """Lazy-load the cross-encoder model (cached after first download)."""
        if self._model_loaded:
            return
        
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
            self._model_loaded = True
            logger.info(f"Loaded cross-encoder model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to load cross-encoder model: {e}")
            self.model = None
            self._model_loaded = True  # Don't retry
    
    def rerank(self, query: str, results: List[Any]) -> List[Any]:
        """Rerank results using cross-encoder."""
        if not results:
            return []
        
        # Lazy-load model
        self._load_model()
        
        if not self.model:
            # Fallback to simple scoring if model unavailable
            return self._simple_rerank(query, results)
        
        try:
            # Prepare pairs
            pairs = [(query, result.text if hasattr(result, 'text') else str(result)) for result in results]
            
            # Score pairs
            scores = self.model.predict(pairs)
            
            # Update scores
            for result, score in zip(results, scores):
                if hasattr(result, 'score'):
                    result.score = float(score)
                elif hasattr(result, '__dict__'):
                    result.__dict__['score'] = float(score)
            
            # Sort by score
            results.sort(key=lambda x: getattr(x, 'score', 0), reverse=True)
            return results
            
        except Exception as e:
            logger.warning(f"Reranking failed: {e}")
            return self._simple_rerank(query, results)
    
    def _simple_rerank(self, query: str, results: List[Any]) -> List[Any]:
        """Simple fallback reranking based on text overlap."""
        query_terms = set(query.lower().split())
        
        for result in results:
            text = result.text if hasattr(result, 'text') else str(result)
            text_terms = set(text.lower().split())
            overlap = len(query_terms.intersection(text_terms))
            
            current_score = getattr(result, 'score', 0)
            if hasattr(result, 'score'):
                result.score = current_score + overlap * 0.1
            elif hasattr(result, '__dict__'):
                result.__dict__['score'] = current_score + overlap * 0.1
        
        results.sort(key=lambda x: getattr(x, 'score', 0), reverse=True)
        return results
