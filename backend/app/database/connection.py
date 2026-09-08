"""
HealthConnect AI - Database Connection
=======================================
Neon DB (serverless PostgreSQL) connection management.

Features:
- Async connection pool
- Connection retry logic
- Health checks
- Connection pooling optimization
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, AsyncAdaptedQueuePool

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DatabaseManager:
    """
    Database connection manager for Neon DB.
    Singleton pattern for connection reuse.
    """
    
    _instance = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker] = None
    _sync_engine = None
    _sync_session_factory: Optional[sessionmaker] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self) -> None:
        """Initialize database connections"""
        if not settings.database.is_configured:
            logger.warning("Database URL not configured")
            return
        
        try:
            # Create async engine
            self._engine = create_async_engine(
                settings.database.database_url,
                poolclass=AsyncAdaptedQueuePool,
                pool_size=settings.database.POOL_SIZE,
                max_overflow=settings.database.MAX_OVERFLOW,
                pool_timeout=settings.database.POOL_TIMEOUT,
                pool_recycle=settings.database.POOL_RECYCLE,
                echo=settings.database.ECHO,
                pool_pre_ping=True,
            )
            
            # Create session factory
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
            
            # Create sync engine for migrations
            self._sync_engine = create_engine(
                settings.database.database_url.replace("postgresql+asyncpg://", "postgresql://"),
                poolclass=QueuePool,
                pool_size=settings.database.POOL_SIZE,
                max_overflow=settings.database.MAX_OVERFLOW,
                pool_pre_ping=True,
            )
            
            self._sync_session_factory = sessionmaker(
                self._sync_engine,
                expire_on_commit=False,
            )
            
            # Test connection
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            if settings.is_production:
                raise
    
    async def close(self) -> None:
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
        
        logger.info("Database connections closed")
    
    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Get async engine"""
        return self._engine
    
    @property
    def session_factory(self) -> Optional[async_sessionmaker]:
        """Get session factory"""
        return self._session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """
        Get database session context manager.
        
        Yields:
            AsyncSession: Database session
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        Execute raw SQL query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Any: Query result
        """
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            return result
    
    async def health_check(self) -> bool:
        """
        Check database health.
        
        Returns:
            bool: True if database is healthy
        """
        try:
            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


def get_database_manager() -> DatabaseManager:
    """Get database manager instance"""
    return DatabaseManager()


async def check_database_connection() -> bool:
    """Check database connection"""
    manager = DatabaseManager()
    return await manager.health_check()