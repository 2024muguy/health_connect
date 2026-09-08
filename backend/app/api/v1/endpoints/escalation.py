"""
HealthConnect AI - Escalation Endpoints
========================================
Escalation management endpoints.

Endpoints:
- POST /escalations: Create escalation
- GET /escalations: List escalations
- GET /escalations/{id}: Get escalation
- PUT /escalations/{id}/assign: Assign escalation
- PUT /escalations/{id}/resolve: Resolve escalation
- GET /escalations/stats: Get escalation statistics
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.deps import get_escalation_service, get_current_user, get_current_admin
from app.schemas.escalation import (
    EscalationCreate,
    EscalationUpdate,
    EscalationResponse,
    EscalationListResponse,
)

from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=EscalationResponse, status_code=status.HTTP_201_CREATED)
async def create_escalation(
    request: EscalationCreate,
    current_user: dict = Depends(get_current_user),
    escalation_service = Depends(get_escalation_service),
):
    """
    Create a new escalation.
    """
    result = await escalation_service.create_escalation(
        conversation_id=str(request.conversation_id) if request.conversation_id else None,
        escalation_type=request.escalation_type.value,
        tier=request.tier.value,
        reason=request.reason,
        priority=request.priority,
        department=request.department,
        description=request.description,
    )
    
    logger.info(
        f"Created escalation: {result.get('escalation_code')} "
        f"by {current_user.get('sub', 'unknown')}"
    )
    
    return result


@router.get("", response_model=EscalationListResponse)
async def list_escalations(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100),
    current_user: dict = Depends(get_current_admin),
    escalation_service = Depends(get_escalation_service),
):
    """
    List escalations (admin only).
    """
    escalations = await escalation_service.list_escalations(
        status=status_filter,
        priority=priority,
        department=department,
        limit=limit,
    )
    
    pending_count = await escalation_service.get_pending_count()
    critical_count = await escalation_service.get_critical_count()
    
    return EscalationListResponse(
        escalations=escalations,
        total=len(escalations),
        page=1,
        page_size=limit,
        pending_count=pending_count,
        critical_count=critical_count,
    )


@router.get("/stats")
async def get_escalation_stats(
    current_user: dict = Depends(get_current_admin),
    escalation_service = Depends(get_escalation_service),
):
    """
    Get escalation statistics (admin only).
    """
    return {
        "pending_count": await escalation_service.get_pending_count(),
        "critical_count": await escalation_service.get_critical_count(),
    }


@router.get("/{escalation_code}", response_model=EscalationResponse)
async def get_escalation(
    escalation_code: str,
    current_user: dict = Depends(get_current_user),
    escalation_service = Depends(get_escalation_service),
):
    """
    Get escalation details.
    """
    escalation = await escalation_service.get_escalation(escalation_code)
    
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found",
        )
    
    return escalation


@router.put("/{escalation_code}/assign")
async def assign_escalation(
    escalation_code: str,
    staff_member: str,
    current_user: dict = Depends(get_current_admin),
    escalation_service = Depends(get_escalation_service),
):
    """
    Assign escalation to staff member (admin only).
    """
    result = await escalation_service.assign_escalation(
        escalation_code=escalation_code,
        staff_member=staff_member,
    )
    
    if result.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found",
        )
    
    return result


@router.put("/{escalation_code}/resolve")
async def resolve_escalation(
    escalation_code: str,
    resolution: str,
    current_user: dict = Depends(get_current_admin),
    escalation_service = Depends(get_escalation_service),
):
    """
    Resolve escalation (admin only).
    """
    result = await escalation_service.resolve_escalation(
        escalation_code=escalation_code,
        resolution=resolution,
        resolved_by=current_user.get("sub", "unknown"),
    )
    
    if result.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found",
        )
    
    return result