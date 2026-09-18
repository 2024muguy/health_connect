"""
HealthConnect AI - Conversation Memory Service
===============================================
Production-grade long-term memory for the chat assistant.

Responsibilities:
- Summarize older turns into a rolling summary (uses Groq)
- Extract structured facts (name, preferences, allergies, goals) into JSON
- Build a compact context card for the LLM prompt
- Persist summary + facts on the Conversation row (idempotent)

Config: config.settings.MemorySettings
"""
from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

import requests

from app.models.conversation import Conversation
from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ============================================================
# Prompt templates
# ============================================================

_SUMMARY_SYSTEM = (
    "You are a clinical-adjacent summarizer for a healthcare assistant. "
    "You will receive a transcript of older conversation turns. Produce a "
    "compact summary in <=120 words that preserves:\n"
    "1. The user's primary goals and questions.\n"
    "2. Any concrete decisions made (bookings, cancellations, transfers).\n"
    "3. Open threads the assistant still needs to resolve.\n"
    "Do NOT invent information. Do NOT include chit-chat."
)

_FACTS_SYSTEM = (
    "Extract structured facts from the conversation as a single JSON object. "
    "Use only the keys the user actually revealed. Allowed keys:\n"
    "  name, age, preferred_language, preferred_location, preferred_time_of_day,\n"
    "  reason_for_visit, insurance_provider, allergies, medications,\n"
    "  prior_no_shows, accessibility_needs, urgency, goals\n"
    "Return ONLY valid JSON. Omit keys not present. No prose, no code fences."
)


# ============================================================
# MemoryService
# ============================================================

class MemoryService:
    """Rolling summary + structured facts for a conversation."""

    def __init__(self) -> None:
        self.enabled = settings.memory.ENABLED
        self.summarize_after = settings.memory.SUMMARIZE_AFTER_TURNS
        self.keep_recent = settings.memory.KEEP_RECENT_TURNS
        self.extract_every = settings.memory.EXTRACT_FACTS_EVERY
        self.max_prompt_turns = settings.memory.MAX_PROMPT_TURNS
        self.model = settings.groq.SUMMARY_MODEL
        self.max_tokens = settings.memory.SUMMARY_MAX_TOKENS
        self.api_key = settings.groq.API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def build_prompt_block(
        self,
        summary: Optional[str],
        facts: Optional[Dict[str, Any]],
        history: List[Dict[str, Any]],
    ) -> str:
        """
        Compose the memory block fed to the LLM prompt.
        Layout: [SUMMARY] + [FACTS] + [LAST K TURNS]
        """
        if not self.enabled:
            return self._render_recent(history, self.max_prompt_turns)

        parts: List[str] = []

        if summary:
            parts.append(f"## Prior conversation summary\n{summary.strip()}")

        if facts:
            facts_lines = [f"- {k}: {v}" for k, v in facts.items() if v not in (None, "", [])]
            if facts_lines:
                parts.append("## Known facts about this user\n" + "\n".join(facts_lines))

        recent = self._render_recent(history, self.keep_recent)
        if recent:
            parts.append("## Recent turns\n" + recent)

        return "\n\n".join(parts).strip()

    async def update_memory(
        self,
        conversation_code: str,
        history: List[Dict[str, Any]],
    ) -> None:
        """
        Update rolling summary and facts if thresholds are met.
        Opens its own DB session — safe to call from anywhere.
        Idempotent — safe to call on every turn.
        """
        if not self.enabled or not history or not conversation_code:
            return

        turns = len(history) // 2  # user+assistant pairs

        # Decide what work is needed
        do_facts = turns > 0 and turns % self.extract_every == 0
        do_summary = turns >= self.summarize_after

        if not do_facts and not do_summary:
            return

        # Open a session, load the conversation, apply changes, commit
        try:
            from app.database.session import AsyncSessionLocal
            from app.models.conversation import Conversation as ConvModel
            from sqlalchemy import select

            async with AsyncSessionLocal() as session:
                r = await session.execute(
                    select(ConvModel).where(ConvModel.conversation_code == conversation_code)
                )
                conv = r.scalar_one_or_none()
                if conv is None:
                    logger.debug(f"update_memory: conversation {conversation_code} not found")
                    return

                changed = False

                # ----- Facts -----
                if do_facts:
                    try:
                        new_facts = self._extract_facts(history)
                        if new_facts:
                            merged = self._merge_facts(self._load_facts(conv), new_facts)
                            conv.facts_json = json.dumps(merged, ensure_ascii=False)
                            logger.info(
                                f"Facts updated ({len(merged)} keys) for conv {conv.id}"
                            )
                            changed = True
                    except Exception as e:
                        logger.warning(f"Fact extraction failed: {e}")

                # ----- Summary -----
                if do_summary:
                    older = history[: -self.keep_recent * 2]
                    if older:
                        try:
                            summary = self._summarize(older)
                            if summary:
                                conv.summary = summary
                                logger.info(
                                    f"Summary updated ({len(summary)} chars) for conv {conv.id}"
                                )
                                changed = True
                        except Exception as e:
                            logger.warning(f"Summarization failed: {e}")

                if changed:
                    await session.commit()
        except Exception as e:
            logger.warning(f"update_memory failed: {e}")

    def load_memory(self, conversation: Optional[Conversation]) -> Dict[str, Any]:
        """Return {summary, facts} for prompt assembly."""
        if not conversation or not self.enabled:
            return {"summary": None, "facts": None}
        return {
            "summary": conversation.summary,
            "facts": self._load_facts(conversation),
        }

    # --------------------------------------------------------
    # Internals
    # --------------------------------------------------------

    def _render_recent(self, history: List[Dict[str, Any]], n: int) -> str:
        if not history:
            return ""
        recent = history[-n * 2 :]
        lines = []
        for m in recent:
            role = (m.get("role") or "user").upper()
            content = (m.get("content") or "").strip().replace("\n", " ")
            if content:
                lines.append(f"{role}: {content[:300]}")
        return "\n".join(lines)

    def _load_facts(self, conversation: Conversation) -> Dict[str, Any]:
        raw = getattr(conversation, "facts_json", None)
        if not raw:
            return {}
        try:
            return json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return {}

    def _merge_facts(self, old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(old or {})
        for k, v in (new or {}).items():
            if v in (None, "", []):
                continue
            # prefer more specific / longer values for strings
            if k in merged and isinstance(merged[k], str) and isinstance(v, str):
                if len(v) > len(merged[k]):
                    merged[k] = v
            else:
                merged[k] = v
        return merged

    def _summarize(self, transcript: List[Dict[str, Any]]) -> Optional[str]:
        text = self._render_recent(transcript, len(transcript))
        if not text:
            return None
        return self._call_groq(_SUMMARY_SYSTEM, text, max_tokens=self.max_tokens)

    def _extract_facts(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Use the last ~8 turns for extraction (fresh facts)
        text = self._render_recent(history, 8)
        if not text:
            return {}
        raw = self._call_groq(_FACTS_SYSTEM, text, max_tokens=250)
        if not raw:
            return {}
        return self._parse_json_safe(raw)

    def _parse_json_safe(self, text: str) -> Dict[str, Any]:
        # strip code fences
        t = re.sub(r"```(?:json)?", "", text).strip("` \n")
        try:
            return json.loads(t)
        except Exception:
            m = re.search(r"\{.*\}", t, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass
        logger.warning(f"Could not parse facts JSON: {t[:120]!r}")
        return {}

    def _call_groq(self, system: str, user: str, max_tokens: int) -> Optional[str]:
        if not self.api_key:
            return None
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
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.2,
                },
                timeout=25,
            )
            if r.status_code != 200:
                logger.warning(f"Groq memory call failed: {r.status_code} {r.text[:200]}")
                return None
            body = r.json()
            return body.get("choices", [{}])[0].get("message", {}).get("content", "").strip() or None
        except Exception as e:
            logger.warning(f"Groq memory call exception: {e}")
            return None


# Module-level singleton
memory_service = MemoryService()
