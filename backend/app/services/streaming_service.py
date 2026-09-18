"""
HealthConnect AI - Streaming Service
=====================================
Streams Groq responses token-by-token for SSE and WebSocket consumers.

Contract:
    stream_groq(prompt_messages, model, max_tokens, temperature)
        -> AsyncIterator[StreamEvent]

StreamEvent fields:
    .type:  "chunk" | "done" | "error"
    .text:  str  (partial content for chunk events)
    .meta:  dict (usage, model, etc. on done)

Usage:
    async for event in stream_groq(messages):
        if event.type == "chunk":
            yield event.text
        elif event.type == "done":
            break
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional

import requests

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


@dataclass
class StreamEvent:
    type: str                                # "chunk" | "done" | "error"
    text: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)


async def stream_groq(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    max_tokens: int = 600,
    temperature: float = 0.3,
    timeout: int = 60,
) -> AsyncIterator[StreamEvent]:
    """
    Stream Groq completion as parsed StreamEvents.

    Runs requests.post(stream=True) in a thread executor to avoid blocking
    the event loop, and yields parsed SSE frames as they arrive.
    """
    api_key = os.getenv("GROQ_API_KEY") or settings.groq.API_KEY
    if not api_key:
        yield StreamEvent(type="error", meta={"reason": "no_api_key"})
        return

    payload = {
        "model": model or os.getenv("GROQ_MODEL") or settings.groq.STREAMING_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()
    done_flag = {"value": False}

    def _worker():
        try:
            with requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=timeout,
            ) as r:
                if r.status_code != 200:
                    body = r.text[:500]
                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        StreamEvent(
                            type="error",
                            meta={"status": r.status_code, "body": body},
                        ),
                    )
                    return

                for line in r.iter_lines(decode_unicode=True):
                    if line is None:
                        continue
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        parsed = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    choices = parsed.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    text = delta.get("content") or ""
                    if text:
                        loop.call_soon_threadsafe(
                            queue.put_nowait,
                            StreamEvent(type="chunk", text=text),
                        )
                    finish = choices[0].get("finish_reason")
                    if finish:
                        loop.call_soon_threadsafe(
                            queue.put_nowait,
                            StreamEvent(type="done", meta={"finish_reason": finish}),
                        )

        except Exception as e:
            logger.warning(f"stream_groq worker error: {e}")
            loop.call_soon_threadsafe(
                queue.put_nowait,
                StreamEvent(type="error", meta={"exception": str(e)}),
            )
        finally:
            done_flag["value"] = True
            loop.call_soon_threadsafe(queue.put_nowait, None)

    loop.run_in_executor(None, _worker)

    while True:
        evt = await queue.get()
        if evt is None:
            if not done_flag["value"]:
                continue
            break
        yield evt
