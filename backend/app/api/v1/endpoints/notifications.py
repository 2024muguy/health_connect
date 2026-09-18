"""
HealthConnect AI - Notifications Endpoints
===========================================
In-memory notifications (replace with DB later).
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

from app.api.deps import get_current_user
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

# In-memory store: { user_id: [notifications] }
_NOTIFICATIONS: Dict[str, List[Dict[str, Any]]] = {}


def _seed_welcome(user_id: str) -> None:
    """Add a welcome notification on first access."""
    if user_id not in _NOTIFICATIONS:
        _NOTIFICATIONS[user_id] = [
            {
                "id": str(uuid.uuid4()),
                "type": "welcome",
                "title": "Welcome to HealthConnect AI",
                "message": "Your care assistant is ready. Try asking about appointments or clinic services.",
                "read": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]


@router.get("")
async def list_notifications(current_user: dict = Depends(get_current_user)):
    """List notifications for the current user."""
    user_id = current_user.get("sub", "anonymous")
    _seed_welcome(user_id)
    items = _NOTIFICATIONS.get(user_id, [])
    return {
        "notifications": sorted(items, key=lambda x: x["created_at"], reverse=True),
        "unread": sum(1 for n in items if not n.get("read")),
    }


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read."""
    user_id = current_user.get("sub", "anonymous")
    for n in _NOTIFICATIONS.get(user_id, []):
        if n["id"] == notification_id:
            n["read"] = True
    return {"status": "ok"}


@router.post("/read-all")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read."""
    user_id = current_user.get("sub", "anonymous")
    for n in _NOTIFICATIONS.get(user_id, []):
        n["read"] = True
    return {"status": "ok"}


@router.post("/seed")
async def seed_test_notifications(current_user: dict = Depends(get_current_user)):
    """Seed test notifications (dev only)."""
    user_id = current_user.get("sub", "anonymous")
    _NOTIFICATIONS.setdefault(user_id, [])
    _NOTIFICATIONS[user_id].extend([
        {
            "id": str(uuid.uuid4()),
            "type": "appointment",
            "title": "Appointment Reminder",
            "message": "Your appointment is tomorrow at 10:00 AM.",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": str(uuid.uuid4()),
            "type": "promo",
            "title": "Free Screening Day",
            "message": "Join us this Saturday for free blood pressure screening.",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ])
    return {"status": "seeded", "count": len(_NOTIFICATIONS[user_id])}
