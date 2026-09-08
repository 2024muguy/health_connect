"""
HealthConnect AI - Chat Endpoints
==================================
Chat and conversation endpoints.

Endpoints:
- POST /chat/message: Send message
- POST /chat/stream: Stream response
- GET /chat/conversations: List conversations
- GET /chat/conversations/{id}: Get conversation
- DELETE /chat/conversations/{id}: End conversation
- POST /chat/feedback: Submit feedback
"""

import json
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service, get_optional_user
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSchema,
    ConversationListResponse,
    FeedbackRequest,
)

from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    chat_service = Depends(get_chat_service),
):
    """
    Send a message and get AI response.
    """
    try:
        response = await chat_service.process_message(
            message=request.message,
            conversation_id=str(request.conversation_id) if request.conversation_id else None,
            session_token=request.session_token,
            user_id=current_user.get("sub") if current_user else None,
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Stream AI response.
    """
    async def generate():
        chat_service = get_chat_service()
        
        async for chunk in chat_service.stream_response(
            message=request.message,
            conversation_id=str(request.conversation_id) if request.conversation_id else None,
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: dict = Depends(get_optional_user),
    chat_service = Depends(get_chat_service),
):
    """
    List conversations.
    """
    conversations = await chat_service.get_active_conversations()
    
    return ConversationListResponse(
        conversations=conversations,
        total=len(conversations),
        page=1,
        page_size=20,
    )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
    chat_service = Depends(get_chat_service),
):
    """
    Get conversation details.
    """
    history = await chat_service.get_conversation_history(conversation_id)
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    return {
        "conversation_id": conversation_id,
        "messages": history,
        "total_messages": len(history),
    }


@router.delete("/conversations/{conversation_id}")
async def end_conversation(
    conversation_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
    chat_service = Depends(get_chat_service),
):
    """
    End a conversation.
    """
    result = await chat_service.end_conversation(conversation_id)
    
    if result.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    return result


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    chat_service = Depends(get_chat_service),
):
    """
    Submit conversation feedback.
    """
    return {
        "status": "received",
        "conversation_id": str(request.conversation_id),
        "satisfaction_score": request.satisfaction_score,
    }