"""
HealthConnect AI - Database Models Package
===========================================
SQLAlchemy ORM models for all database tables.

Models:
- Base: Abstract base model
- Patient: Patient information
- Appointment: Appointment records
- Conversation: Chat conversations
- Message: Individual messages
- Escalation: Escalation tickets
- KnowledgeChunk: RAG knowledge chunks
- Analytics: Analytics events
"""

from app.models.base import Base, TimestampMixin
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.escalation import Escalation
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.analytics import AnalyticsEvent

__all__ = [
    "Base",
    "TimestampMixin",
    "Patient",
    "Appointment",
    "Conversation",
    "Message",
    "Escalation",
    "KnowledgeChunk",
    "AnalyticsEvent",
]