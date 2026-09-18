"""
HealthConnect AI - Tool Registry
=================================
Defines tools callable by the multi-agent orchestrator.

Each tool has:
    name        - stable identifier used by the router
    description - natural-language description for the LLM
    async fn    - the callable

The registry is intentionally simple: agents ask for a tool by name,
the registry runs it and returns the result. No external tool-calling
framework required.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


ToolFn = Callable[..., Awaitable[Dict[str, Any]]]


@dataclass
class Tool:
    name: str
    description: str
    fn: ToolFn


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, name: str, description: str, fn: ToolFn) -> None:
        self._tools[name] = Tool(name=name, description=description, fn=fn)
        logger.info(f"Tool registered: {name}")

    def list(self) -> Dict[str, Tool]:
        return dict(self._tools)

    def describe(self) -> str:
        if not self._tools:
            return ""
        return "\n".join(f"- {t.name}: {t.description}" for t in self._tools.values())

    async def call(self, name: str, **kwargs) -> Dict[str, Any]:
        tool = self._tools.get(name)
        if not tool:
            return {"ok": False, "error": f"unknown tool: {name}"}
        try:
            result = await tool.fn(**kwargs)
            return {"ok": True, "result": result}
        except Exception as e:
            logger.warning(f"tool {name} failed: {e}")
            return {"ok": False, "error": str(e)}


tool_registry = ToolRegistry()


# ============================================================
# Built-in tools
# ============================================================

async def tool_knowledge_search(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Search the KB."""
    from app.rag.retriever import HybridRetriever
    retriever = HybridRetriever()
    results = await retriever.retrieve(query=query, top_k=top_k, retrieval_method="hybrid")
    return {
        "count": len(results or []),
        "chunks": [
            {"chunk_id": r.chunk_id, "score": r.score, "text": r.text[:300]}
            for r in (results or [])
        ],
    }


async def tool_check_availability(date: str, service: Optional[str] = None) -> Dict[str, Any]:
    """Return available time slots for a given date."""
    # Reuse the appointment_service if possible; otherwise return placeholders
    try:
        from app.services.appointment_service import AppointmentService
        svc = AppointmentService()
        slots = await svc.get_availability(date) if hasattr(svc, "get_availability") else []
        return {"date": date, "slots": slots}
    except Exception as e:
        return {"date": date, "slots": [], "note": f"availability unavailable: {e}"}


async def tool_create_appointment(
    patient_id: str,
    appointment_type: str,
    scheduled_datetime: str,
    duration_minutes: int = 30,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an appointment (called only after user confirmation)."""
    from app.services.appointment_service import AppointmentService
    from datetime import datetime
    svc = AppointmentService()
    when = datetime.fromisoformat(scheduled_datetime)
    return await svc.create_appointment(
        patient_id=patient_id,
        appointment_type=appointment_type,
        scheduled_datetime=when,
        duration_minutes=duration_minutes,
        reason=reason,
    )


async def tool_escalate_to_human(reason: str, session_token: Optional[str] = None) -> Dict[str, Any]:
    """Create a human-handoff ticket."""
    from app.services.audit_log import audit
    audit("escalation", reason=reason, session=session_token)
    return {"status": "escalated", "reason": reason}


def register_builtin_tools() -> None:
    tool_registry.register("knowledge_search", "Search the clinic knowledge base", tool_knowledge_search)
    tool_registry.register("check_availability", "List appointment slots for a date", tool_check_availability)
    tool_registry.register("create_appointment", "Book an appointment after user confirmation", tool_create_appointment)
    tool_registry.register("escalate_to_human", "Hand off to a human staff member", tool_escalate_to_human)


register_builtin_tools()
