"""
HealthConnect AI - Database Session
====================================
Database session management for SQLAlchemy.
"""

import os
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

# Get database URL
database_url = os.getenv("NEON_DATABASE_URL", "") or os.getenv("DATABASE_URL", "")

if not database_url:
    database_url = "sqlite:///./health_connect.db"
    logger.warning("No database URL found, using SQLite fallback")

# Convert to async URL
if database_url.startswith("postgresql://"):
    async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
elif database_url.startswith("sqlite:///"):
    async_database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_database_url = database_url

logger.info(f"Using database: {async_database_url.split('@')[-1] if '@' in async_database_url else async_database_url}")

# Synchronous engine
engine = create_engine(database_url, pool_pre_ping=True, echo=settings.database.ECHO)

# Session factories
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Async engine
async_engine = create_async_engine(async_database_url, pool_pre_ping=True, echo=settings.database.ECHO)

# For backwards compatibility
Base = None  # Will be set by models


def get_session() -> Generator[Session, None, None]:
    """Get synchronous database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


__all__ = [
    "engine",
    "async_engine",
    "SessionLocal",
    "AsyncSessionLocal",
    "Base",
    "get_session",
    "get_async_session",
]
