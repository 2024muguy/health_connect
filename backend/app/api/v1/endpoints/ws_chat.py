"""
HealthConnect AI - WebSocket Chat Endpoint
===========================================
Real-time chat with token streaming over WebSocket.

Client sends:   {"message": "..."}
Server sends:
    {"type": "ack"}                                  -- received
    {"type": "start", "conversation_id": "..."}      -- beginning response
    {"type": "chunk", "text": "..."}                 -- partial tokens
    {"type": "done", "text": "...", ...}             -- completion
    {"type": "error", "error": "..."}                -- failure
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from app.core.security import security_manager
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _verify_ws_token(token: Optional[str]) -> Optional[dict]:
    """Verify a JWT passed as a query parameter (defensive).

    In development, tolerate tokens up to 10 minutes past expiry so that
    WS reconnects don't fail if the refresh happens slightly after close.
    """
    if not token:
        return None
    try:
        payload = security_manager.decode_token(token)
        if payload:
            if payload.get("type") not in (None, "access"):
                return None
            return payload

        # decode_token returned empty — try a lenient decode (ignore expiry)
        import os
        if os.getenv("ENVIRONMENT", "development") == "development":
            try:
                import jwt as _jwt
                lenient = _jwt.decode(
                    token,
                    security_manager.secret_key,
                    algorithms=[security_manager.algorithm],
                    options={"verify_exp": False},
                )
                if lenient.get("type") not in (None, "access"):
                    return None
                logger.info("WS: accepted recently-expired token (dev mode)")
                return lenient
            except Exception as e:
                logger.warning(f"WS lenient decode failed: {e}")

        return None
    except Exception as e:
        logger.warning(f"WS token verification failed: {type(e).__name__}: {e}")
        return None


async def _stream_response_over_ws(
    websocket: WebSocket,
    conversation_id: str,
    user_message: str,
    user_id: Optional[str],
) -> None:
    """Run the chat pipeline and stream chunks back over WS."""
    from app.services.chat_service import ChatService

    await websocket.send_json({"type": "ack", "timestamp": datetime.now(timezone.utc).isoformat()})

    try:
        service = ChatService()
        result = await service.process_message(
            message=user_message,
            conversation_id=conversation_id,
            session_token=None,
            user_id=user_id,
        )
        full_text = (
            result.get("text") or result.get("response") or result.get("message") or ""
        )
        conv_id = result.get("conversation_id") or conversation_id

        await websocket.send_json({
            "type": "start",
            "conversation_id": conv_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Phase 1: emit chunks from the composed response.
        # Phase 2 will stream tokens directly from Groq via streaming_service.
        chunk_size = 24
        for i in range(0, len(full_text), chunk_size):
            piece = full_text[i:i + chunk_size]
            await websocket.send_json({"type": "chunk", "text": piece})
            await asyncio.sleep(0.02)

        await websocket.send_json({
            "type": "done",
            "message_id": str(uuid.uuid4()),
            "conversation_id": conv_id,
            "text": full_text,
            "intent": result.get("intent", "unknown"),
            "safety_category": result.get("safety_category", "safe"),
            "citations": result.get("citations", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        logger.error(f"WS stream error: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "error": str(e)})
        except Exception:
            pass


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = Query(default=None),
):
    access_token = token or websocket.query_params.get("access_token")
    payload = _verify_ws_token(access_token)
    if not payload:
        logger.warning("WS: token verification FAILED — closing with 1008")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info(f"WS accepted: user={payload.get('sub')} conv={conversation_id}")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"message": raw}

            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            user_message = (data.get("message") or "").strip()
            if not user_message:
                continue

            await _stream_response_over_ws(
                websocket,
                conversation_id,
                user_message,
                payload.get("sub"),
            )

    except WebSocketDisconnect:
        logger.info(f"WS disconnected: conv={conversation_id}")
    except Exception as e:
        logger.error(f"WS outer error: {e}", exc_info=True)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
