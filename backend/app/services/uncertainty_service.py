"""
HealthConnect AI - Uncertainty Service
=======================================
Scores each response on confidence and gates low-confidence answers.

Two signals:
  1. retrieval_score  = max similarity across retrieved chunks
  2. judge_score      = LLM judge (KB-grounding + helpfulness), 0.0-1.0

If combined < threshold, replace the response with LOW_CONFIDENCE_TEMPLATE
and mark requires_human=True.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

import requests

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


_JUDGE_SYSTEM = (
    "You are an evaluator for a healthcare assistant. Score the ASSISTANT "
    "response on a 0.0-1.0 scale for these criteria, then output ONLY a JSON "
    "object with these keys:\n"
    "  grounding:  how well the response sticks to the provided context\n"
    "  helpfulness: did the response actually answer the user's question\n"
    "  safety:     does the response avoid medical advice/diagnosis\n"
    "  tone:       is it warm, clear, concise\n"
    "  overall:    combined score\n"
    "No prose, no code fences. JSON only."
)


class UncertaintyService:
    def __init__(self) -> None:
        self.enabled = settings.uncertainty.ENABLED
        self.min_retrieval = settings.uncertainty.MIN_RETRIEVAL_SCORE
        self.min_judge = settings.uncertainty.MIN_JUDGE_SCORE
        self.template = settings.uncertainty.LOW_CONFIDENCE_TEMPLATE
        self.model = settings.groq.JUDGE_MODEL
        self.api_key = settings.groq.API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def score_and_gate(
        self,
        response_text: str,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Returns:
            {
              "response": str,          # original or replaced
              "confidence": float,      # 0.0-1.0
              "retrieval_score": float,
              "judge_score": Optional[float],
              "gated": bool,
            }
        """
        if not self.enabled:
            return {
                "response": response_text,
                "confidence": 1.0,
                "retrieval_score": 1.0,
                "judge_score": None,
                "gated": False,
            }

        retrieval_score = self._retrieval_score(retrieved_chunks)
        judge_result = self._judge(response_text, query, retrieved_chunks)
        judge_score = judge_result.get("overall") if judge_result else None

        confidence = self._combine(retrieval_score, judge_score)

        gated = confidence < self.min_judge and retrieval_score < self.min_retrieval

        return {
            "response": self.template if gated else response_text,
            "confidence": round(confidence, 3),
            "retrieval_score": round(retrieval_score, 3),
            "judge_score": judge_score,
            "gated": gated,
        }

    # ------------------------------------------------------------------

    def _retrieval_score(self, chunks: List[Dict[str, Any]]) -> float:
        if not chunks:
            return 0.0
        scores = [float(c.get("score") or 0.0) for c in chunks]
        return max(scores) if scores else 0.0

    def _combine(self, ret: float, judge: Optional[float]) -> float:
        if judge is None:
            return ret
        return round(0.4 * ret + 0.6 * judge, 3)

    def _judge(
        self,
        response_text: str,
        query: str,
        chunks: List[Dict[str, Any]],
    ) -> Optional[Dict[str, float]]:
        if not self.api_key or not response_text:
            return None

        ctx = " || ".join((c.get("text") or "")[:200] for c in chunks[:3]) or "(no context)"
        user = (
            f"CONTEXT: {ctx}\n\n"
            f"USER QUESTION: {query}\n\n"
            f"ASSISTANT RESPONSE: {response_text}\n\n"
            "Return JSON only."
        )

        try:
            r = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": _JUDGE_SYSTEM},
                        {"role": "user", "content": user},
                    ],
                    "max_tokens": 120,
                    "temperature": 0.0,
                },
                timeout=15,
            )
            if r.status_code != 200:
                return None
            content = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return self._parse(content)
        except Exception as e:
            logger.warning(f"judge call failed: {e}")
            return None

    def _parse(self, text: str) -> Optional[Dict[str, float]]:
        t = re.sub(r"```(?:json)?", "", text).strip("` \n")
        try:
            data = json.loads(t)
        except Exception:
            m = re.search(r"\{.*\}", t, re.DOTALL)
            if not m:
                return None
            try:
                data = json.loads(m.group(0))
            except Exception:
                return None
        out = {}
        for k in ("grounding", "helpfulness", "safety", "tone", "overall"):
            if k in data:
                try:
                    out[k] = float(data[k])
                except Exception:
                    pass
        return out or None


uncertainty_service = UncertaintyService()
