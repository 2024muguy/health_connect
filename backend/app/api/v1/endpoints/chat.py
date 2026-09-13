"""
HealthConnect AI - Chat Endpoints
==================================
"""

import json
import uuid as uuid_module
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_chat_service, get_optional_user
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
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
            response=str(response_text),
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
