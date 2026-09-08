"""
HealthConnect AI - Database Session
====================================
SQLAlchemy session management.

Provides:
- Synchronous session factory
- Asynchronous session factory
- Session dependency for FastAPI
"""

from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Base class for all models
Base = declarative_base()

# Database URL
database_url = settings.database.database_url

# Async engine
async_engine = create_async_engine(
    database_url,
    pool_size=settings.database.POOL_SIZE,
    max_overflow=settings.database.MAX_OVERFLOW,
    pool_timeout=settings.database.POOL_TIMEOUT,
    pool_recycle=settings.database.POOL_RECYCLE,
    echo=settings.database.ECHO,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Sync engine (for migrations and scripts)
sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
engine = create_engine(
    sync_database_url,
    pool_size=settings.database.POOL_SIZE,
    max_overflow=settings.database.MAX_OVERFLOW,
    echo=settings.database.ECHO,
    pool_pre_ping=True,
)

# Sync session factory
SessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for sync database session.
    
    Yields:
        Session: Database session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_db() -> None:
    """Initialize database tables"""
    from app.models import Base as ModelBase
    
    async with async_engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)
    
    logger.info("Database tables created")


async def drop_db() -> None:
    """Drop all database tables"""
    from app.models import Base as ModelBase
    
    async with async_engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
    
    logger.info("Database tables dropped")