"""Cross-encoder reranker — improves RAG precision."""
from __future__ import annotations
import time
from typing import List, Any

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RerankerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
            cls._instance.model = None
        return cls._instance

    def _load(self):
        if self._loaded:
            return
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(
                settings.rag.RERANKER_MODEL,
                max_length=512,
            )
            self._loaded = True
            logger.info(f"✅ Reranker loaded: {settings.rag.RERANKER_MODEL}")
        except Exception as e:
            logger.warning(f"Reranker load failed: {e}")
            self._loaded = True  # do not retry

    def rerank(self, query: str, candidates: List[Any], keep: int) -> List[Any]:
        """
        Score each candidate with a cross-encoder and return top-k.

        Each candidate must have a `.text` attribute.
        """
        if not settings.rag.RERANKER_ENABLED or not candidates:
            return candidates[:keep]

        self._load()
        if self.model is None:
            return candidates[:keep]

        try:
            pairs = [(query, c.text) for c in candidates]
            scores = self.model.predict(pairs, show_progress_bar=False)

            ranked = sorted(
                zip(scores, candidates),
                key=lambda x: float(x[0]),
                reverse=True,
            )
            top = [c for _, c in ranked[:keep]]
            logger.info(
                f"Reranked {len(candidates)} → {len(top)} "
                f"(top score {float(ranked[0][0]):.3f})"
            )
            return top
        except Exception as e:
            logger.warning(f"Rerank failed: {e}")
            return candidates[:keep]


reranker_service = RerankerService()
