"""
HealthConnect AI - Models Package
==================================
Database models for HealthConnect AI.

Import order matters for SQLAlchemy relationships.
"""

# Import Base first
from app.models.base import BaseModel, SoftDeleteMixin, Base

# Import Patient first (others depend on it)
from app.models.patient import Patient

# Import Appointment (depends on Patient)
from app.models.appointment import Appointment

# Import Conversation and Message
from app.models.conversation import Conversation
from app.models.message import Message

# Import Knowledge Chunk
from app.models.knowledge_chunk import KnowledgeChunk

# Import Escalation
from app.models.escalation import Escalation

__all__ = [
    "Base",
    "BaseModel",
    "SoftDeleteMixin",
    "Patient",
    "Appointment",
    "Conversation",
    "Message",
    "KnowledgeChunk",
    "Escalation",
]
