"""
HealthConnect AI - Database Package
====================================
Database connection and session management.

This package provides:
- Database connection management
- SQLAlchemy session management
- Connection pooling for Neon DB
"""

from app.database.connection import DatabaseManager, get_database_manager
from app.database.session import (
    get_session,
    get_async_session,
    SessionLocal,
    AsyncSessionLocal,
    Base,
    engine,
    async_engine,
)

__all__ = [
    "DatabaseManager",
    "get_database_manager",
    "get_session",
    "get_async_session",
    "SessionLocal",
    "AsyncSessionLocal",
    "Base",
    "engine",
    "async_engine",
]