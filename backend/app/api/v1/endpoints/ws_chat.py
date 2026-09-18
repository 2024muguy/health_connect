"""
HealthConnect AI - WebSocket Chat Endpoint
===========================================
Real-time chat via WebSocket.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from typing import Optional
import json
import uuid
from datetime import datetime, timezone

from app.core.security import security_manager
# ChatService imported lazily inside the handler to avoid circular imports
from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


def _verify_ws_token(token: Optional[str]) -> Optional[dict]:
    """Verify a JWT passed as a query parameter (defensive)."""
    if not token:
        return None
    try:
        # Prefer decode_token which doesn't raise custom exceptions
        payload = security_manager.decode_token(token)
        if not payload:
            return None
        # Optional type check
        if payload.get("type") not in (None, "access"):
            logger.warning(f"WS token type is {payload.get('type')}, expected access")
            return None
        return payload
    except Exception as e:
        logger.warning(f"WS token verification failed: {type(e).__name__}: {e}")
        return None


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = Query(default=None),
):
    logger.info(f"WS: incoming request for conv={conversation_id}")

    # Try both `token` and `access_token` query params
    access_token = token or websocket.query_params.get("access_token")
    logger.info(f"WS: token present={bool(access_token)}, prefix={access_token[:20] if access_token else None}")

    payload = _verify_ws_token(access_token)
    if not payload:
        logger.warning("WS: token verification FAILED — closing with 1008")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    logger.info(f"WS: token OK, user={payload.get('sub')}")

    try:
        await websocket.accept()
        logger.info(f"WS: accepted connection for conv={conversation_id}")
    except Exception as e:
        logger.error(f"WS: accept() failed: {e}", exc_info=True)
        return

    try:
        while True:
            raw = await websocket.receive_text()
            logger.info(f"WS: received: {raw[:80]}")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"message": raw}

            user_message = (data.get("message") or "").strip()
            if not user_message:
                continue

            try:
                from app.services.chat_service import ChatService
                service = ChatService()
                result = await service.process_message(
                    message=user_message,
                    conversation_id=conversation_id,
                    session_token=None,
                    user_id=payload.get("sub"),
                )
                await websocket.send_json({
                    "type": "message",
                    "message_id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "response": result.get("text") or result.get("response") or result.get("message") or "",
                    "intent": result.get("intent", "unknown"),
                    "safety_category": result.get("safety_category", "safe"),
                    "citations": result.get("citations", []),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as e:
                logger.error(f"WS chat error: {e}", exc_info=True)
                await websocket.send_json({"type": "error", "error": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WS: disconnected for conv={conversation_id}")
    except Exception as e:
        logger.error(f"WS: outer error: {e}", exc_info=True)


    payload = _verify_ws_token(access_token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.info("WS connection rejected: invalid token")
        return

    await websocket.accept()
    logger.info(f"WS connected: user={payload.get('sub')} conv={conversation_id}")

    from app.services.chat_service import ChatService
    service = ChatService()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = {"message": raw}

            user_message = (data.get("message") or "").strip()
            if not user_message:
                continue

            # Optional: send an "ack"
            await websocket.send_json({
                "type": "ack",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            # Process the message through the chat service
            try:
                result = await service.process_message(
                    message=user_message,
                    conversation_id=conversation_id,
                    session_token=None,
                    user_id=payload.get("sub"),
                )
                await websocket.send_json({
                    "type": "message",
                    "message_id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "response": result.get("text") or result.get("response") or result.get("message") or "",
                    "intent": result.get("intent", "unknown"),
                    "safety_category": result.get("safety_category", "safe"),
                    "citations": result.get("citations", []),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as e:
                logger.error(f"WS chat error: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "error": str(e),
                })

    except WebSocketDisconnect:
        logger.info(f"WS disconnected: conv={conversation_id}")
    except Exception as e:
        logger.error(f"WS error: {e}", exc_info=True)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
