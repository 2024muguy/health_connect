"""
HealthConnect AI - Chat Endpoints
==================================
"""

import json
import uuid as uuid_module
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.streaming_service import stream_groq
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service, get_optional_user, get_current_user
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()




def _clean_text(text: str) -> str:
    """Fix mojibake from UTF-8 being misread as CP1252 and normalize."""
    if not text:
        return text

    # The mojibake triples we see are each 3 Python chars:
    #   0x00e2 (a-circumflex) + 0x20ac (euro) + one of {0x00a2, 0x00af, ...}
    # We replace each with the intended UTF-8 character.
    fixes = [
        ("\u00e2\u20ac\u00a2", "\u2022"),   # bullet
        ("\u00e2\u20ac\u00af", " "),         # narrow no-break space
        ("\u00e2\u20ac\u00a0", " "),         # non-breaking space
        ("\u00e2\u20ac\u02dc", "\u2018"),   # left single quote
        ("\u00e2\u20ac\u2122", "\u2019"),   # right single quote
        ("\u00e2\u20ac\u0153", "\u201c"),   # left double quote
        ("\u00e2\u20ac\u009d", "\u201d"),   # right double quote
        ("\u00e2\u20ac\u201c", "\u2013"),   # en dash
        ("\u00e2\u20ac\u201d", "\u2014"),   # em dash
        ("\u00e2\u20ac\u2018", "\u2011"),   # non-breaking hyphen
        ("\u00e2\u20ac\u00a6", "\u2026"),   # ellipsis
        ("\u00c3\u00a9", "\u00e9"),
        ("\u00c3\u00a8", "\u00e8"),
    ]
    for bad, good in fixes:
        text = text.replace(bad, good)

    # Aggressive fallback: any remaining 0x00e2 0x20ac X sequence is garbage.
    import re as _re
    text = _re.sub("\u00e2\u20ac[\u0080-\u00ff]", "", text)

    # Strip zero-width and control chars
    text = "".join(ch for ch in text if ch in "\n\t" or ord(ch) >= 32)
    text = _re.sub(r" {3,}", "  ", text)
    return text


    # Aggressive first pass: strip any 3-char sequence that starts with 0x00e2
    # followed by 0x20ac (UTF-8 Euro sign) and any byte in 0x80-0xff range.
    # This is the mojibake family we see from CP1252-misdecoded UTF-8.
    import re as _re
    text = _re.sub(r"\u00e2\u20ac[\u0080-\u00ff]", "", text)
    text = text.replace("\u00c3\u00a9", "\u00e9").replace("\u00c3\u00a8", "\u00e8")
    # CP1252-misread-UTF-8 triples (each is exactly 3 characters, e.g. "a with circumflex" + "euro sign" + "bullet")
    replacements = {
        # bullet: 'â€¢'  (0x00e2 0x20ac 0x00a2)
        "\u00e2\u20ac\u00a2": "\u2022",
        # narrow no-break space: 'â€¯'  (0x00e2 0x20ac 0x00af)
        "\u00e2\u20ac\u00af": " ",
        # non-breaking space: 'â€ '  (0x00e2 0x20ac 0x00a0)
        "\u00e2\u20ac\u00a0": " ",
        # left single quote: 'â€˜'
        "\u00e2\u20ac\u02dc": "\u2018",
        # right single quote: 'â€™'
        "\u00e2\u20ac\u2122": "\u2019",
        # left double quote: 'â€œ'
        "\u00e2\u20ac\u0153": "\u201c",
        # right double quote: 'â€\x9d'
        "\u00e2\u20ac\u009d": "\u201d",
        # en dash: 'â€“'
        "\u00e2\u20ac\u201c": "\u2013",
        # em dash: 'â€”'
        "\u00e2\u20ac\u201d": "\u2014",
        # non-breaking hyphen: 'â€‘'
        "\u00e2\u20ac\u2018": "\u2011",
        # ellipsis: 'â€¦'
        "\u00e2\u20ac\u00a6": "\u2026",
        # é
        "\u00c3\u00a9": "\u00e9",
        # è
        "\u00c3\u00a8": "\u00e8",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # Fix specific UTF-8-mojibake triples (do this BEFORE the general strip)
    SPECIFIC = {
        "\u00e2\u20ac\u00af": " ",       # '\u00e2\u20ac\u00af' -> narrow space -> normal space
        "\u00e2\u20ac\u00a0": " ",
        "\u00e2\u20ac\u2019": "'",
        "\u00e2\u20ac\u2018": "'",
        "\u00e2\u20ac\u201c": '"',
        "\u00e2\u20ac\u009d": '"',
        "\u00e2\u20ac\u2013": "-",
        "\u00e2\u20ac\u2014": "-",
        "\u00e2\u20ac\u00a6": "...",
        "\u00c3\u00a9": "e",
        "\u00c3\u00a8": "e",
    }
    for bad, good in SPECIFIC.items():
        text = text.replace(bad, good)

    # Replace any remaining non-printable control chars
    text = ''.join(ch for ch in text if ch == '\n' or ch == '\t' or ord(ch) >= 32)
    # Final mojibake catch-all: remove any lingering "\u00e2\u20ac" family
    import re as _re
    text = _re.sub(r"\u00e2\u20ac[\u0080-\u20ff]", "", text)
    # Collapse repeated spaces (but keep newlines)
    text = _re.sub(r" {3,}", "  ", text)
    return text


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    chat_service = Depends(get_chat_service),
):
    """Send a message and get AI response."""
    try:
        response = await chat_service.process_message(
            message=request.message,
            conversation_id=str(request.conversation_id) if request.conversation_id else None,
            session_token=request.session_token,
            user_id=current_user.get("sub") if current_user else None,
        )
        
        # Extract response data from dict or AgentResult
        if isinstance(response, dict):
            response_data = response
        elif hasattr(response, 'output') and isinstance(response.output, dict):
            response_data = response.output
        else:
            response_data = {}
        
        # Get the response text - check all possible field names
        response_text = (
            response_data.get("text") or
            response_data.get("response") or
            response_data.get("answer") or
            "I apologize, but I couldn't generate a response. Please try again."
        )
        
        # Get UUIDs
        message_id = response_data.get("message_id")
        if isinstance(message_id, str):
            try:
                message_id = uuid_module.UUID(message_id)
            except ValueError:
                message_id = uuid_module.uuid4()
        else:
            message_id = uuid_module.uuid4()
        
        conversation_id = response_data.get("conversation_id")
        if isinstance(conversation_id, str):
            try:
                conversation_id = uuid_module.UUID(conversation_id)
            except ValueError:
                conversation_id = uuid_module.uuid4()
        else:
            conversation_id = uuid_module.uuid4()
        
        # Get intent
        intent = response_data.get("intent", "general_faq")
        if isinstance(intent, dict):
            intent = intent.get("intent", "general_faq")
        
        # Get safety
        safety_category = response_data.get("safety_category", "safe")
        if isinstance(safety_category, dict):
            safety_category = safety_category.get("safety_category", "safe")
        
        # Clean citations - ensure all fields are strings
        raw_citations = response_data.get("citations", [])
        citations = []
        for citation in raw_citations:
            if isinstance(citation, dict):
                cleaned = {}
                for key, value in citation.items():
                    if value is None:
                        cleaned[key] = ""
                    elif not isinstance(value, str):
                        cleaned[key] = str(value)
                    else:
                        cleaned[key] = value
                citations.append(cleaned)
            elif isinstance(citation, str):
                citations.append({"source": citation})
        
        # Build response
        chat_response = ChatResponse(
            message_id=message_id,
            conversation_id=conversation_id,
            response=_clean_text(str(response_text)),
            intent=str(intent),
            intent_confidence=float(response_data.get("intent_confidence", 0.5)),
            safety_category=str(safety_category),
            safety_score=float(response_data.get("safety_score", 1.0)),
            action_performed=str(response_data.get("action_performed")) if response_data.get("action_performed") else None,
            requires_human=bool(response_data.get("requires_human", False)),
            citations=citations,
            processing_time_ms=float(response_data.get("processing_time_ms", 0)),
        )
        
        return chat_response
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )
        response_text = _clean_text(response_text)



# ============================================
# Conversation Management Endpoints
# ============================================

@router.get("/conversations")
async def list_conversations(
    current_user: dict = Depends(get_current_user),
):
    """List conversations for the current user."""
    from app.services.chat_service import ChatService
    service = ChatService()
    conversations = await service.get_active_conversations()
    return {
        "conversations": conversations,
        "total": len(conversations),
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a conversation by ID with its messages."""
    from app.services.chat_service import ChatService
    service = ChatService()
    history = await service.get_conversation_history(conversation_id, limit=100)

    if not history:
        # Return an empty conversation instead of 404 so the frontend can start fresh
        return {
            "conversation_id": conversation_id,
            "messages": [],
            "total": 0,
        }

    return {
        "conversation_id": conversation_id,
        "messages": history,
        "total": len(history),
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete (end) a conversation."""
    from app.services.chat_service import ChatService
    service = ChatService()
    result = await service.end_conversation(conversation_id)
    return result


# ============================================================
# Streaming endpoint — token-by-token SSE
# ============================================================

@router.post("/message/stream")
async def send_message_stream(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    chat_service = Depends(get_chat_service),
):
    """
    Stream a chat response token-by-token as Server-Sent Events.

    Event shapes (one JSON object per `data:` line):
      {"type": "start",   "conversation_id": "..."}
      {"type": "chunk",   "text": "partial token(s)"}
      {"type": "done",    "text": "full response", "conversation_id": "..."}
      {"type": "error",   "error": "message"}
    """

    async def event_source():
        # Send the opening frame right away so proxies don't buffer
        yield _sse({"type": "start", "conversation_id": str(request.conversation_id or "")})

        try:
            # 1. Run the pipeline once to get retrieval + intent + memory.
            #    We do NOT use its generated text — we use the context it retrieved
            #    to build a fresh streaming completion.
            result = await chat_service.process_message(
                message=request.message,
                conversation_id=str(request.conversation_id) if request.conversation_id else None,
                session_token=request.session_token,
                user_id=current_user.get("sub") if current_user else None,
            )

            response_text = (
                result.get("text")
                or result.get("response")
                or result.get("message")
                or ""
            )
            conversation_id = result.get("conversation_id") or ""

            # 2. For the streaming path, emit the fully-composed response as chunks.
            #    (A true token stream requires ConversationAgent to expose the Groq
            #    streaming iterator. That is Phase 2 below.)
            chunk_size = 24
            for i in range(0, len(response_text), chunk_size):
                piece = response_text[i:i + chunk_size]
                yield _sse({"type": "chunk", "text": piece})
                await __import__("asyncio").sleep(0.02)

            yield _sse({
                "type": "done",
                "text": response_text,
                "conversation_id": conversation_id,
                "intent": result.get("intent", "unknown"),
                "safety_category": result.get("safety_category", "safe"),
                "citations": result.get("citations", []),
            })
        except Exception as e:
            logger.warning(f"SSE stream failed: {e}")
            yield _sse({"type": "error", "error": str(e)})

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def _sse(payload: dict) -> str:
    """Serialize a dict as a single SSE frame."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
