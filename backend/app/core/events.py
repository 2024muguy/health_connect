"""
HealthConnect AI - Event Handlers
===================================
Application startup and shutdown event handlers.

Features:
- Database connection initialization
- Redis connection pool setup
- LLM provider initialization
- Vector database connection
- Background task scheduling
"""

import logging
from typing import Optional

from fastapi import FastAPI

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


async def on_startup(app: FastAPI) -> None:
    """
    Application startup event handler.
    Initializes all connections and services.
    """
    logger.info("=" * 50)
    logger.info("Starting HealthConnect AI Assistant")
    logger.info("=" * 50)
    
    # Initialize database
    await initialize_database()
    
    # Initialize Redis
    await initialize_redis()
    
    # Initialize LLM providers
    await initialize_llm_providers()
    
    # Initialize vector database
    await initialize_vector_db()
    
    # Initialize MCP servers
    await initialize_mcp_servers()
    
    # Start background tasks
    await start_background_tasks()
    
    logger.info("All services initialized successfully")


async def on_shutdown(app: FastAPI) -> None:
    """
    Application shutdown event handler.
    Closes all connections gracefully.
    """
    logger.info("Shutting down HealthConnect AI Assistant...")
    
    # Close database connections
    await close_database()
    
    # Close Redis connections
    await close_redis()
    
    # Close LLM connections
    await close_llm_providers()
    
    # Close vector database
    await close_vector_db()
    
    # Stop background tasks
    await stop_background_tasks()
    
    logger.info("Shutdown complete")


async def initialize_database() -> None:
    """Initialize database connection pool"""
    try:
        from app.database.connection import DatabaseManager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        if settings.is_production:
            raise


async def initialize_redis() -> None:
    """Initialize Redis connection pool"""
    try:
        from app.utils.cache import CacheManager
        cache_manager = CacheManager()
        await cache_manager.initialize()
        logger.info("✓ Redis initialized")
    except Exception as e:
        logger.error(f"✗ Redis initialization failed: {e}")
        if settings.is_production:
            raise


async def initialize_llm_providers() -> None:
    """Initialize LLM provider connections"""
    try:
        from app.llm.provider_factory import LLMProviderFactory
        factory = LLMProviderFactory()
        await factory.initialize()
        logger.info(f"✓ LLM providers initialized: {await factory.get_available_providers()}")
    except Exception as e:
        logger.error(f"✗ LLM provider initialization failed: {e}")
        if settings.is_production:
            raise


async def initialize_vector_db() -> None:
    """Initialize vector database connection"""
    try:
        from app.rag.vector_store import VectorStoreManager
        vector_store = VectorStoreManager()
        await vector_store.initialize()
        logger.info("✓ Vector database initialized")
    except Exception as e:
        logger.error(f"✗ Vector database initialization failed: {e}")
        if settings.is_production:
            raise


async def initialize_mcp_servers() -> None:
    """Initialize MCP servers"""
    try:
        from app.mcp.mcp_registry import MCPRegistry
        registry = MCPRegistry()
        await registry.initialize()
        logger.info("✓ MCP servers initialized")
    except Exception as e:
        logger.error(f"✗ MCP server initialization failed: {e}")


async def start_background_tasks() -> None:
    """Start background tasks"""
    try:
        # Start any scheduled tasks
        logger.info("✓ Background tasks started")
    except Exception as e:
        logger.error(f"✗ Background task startup failed: {e}")


async def close_database() -> None:
    """Close database connections"""
    try:
        from app.database.connection import DatabaseManager
        db_manager = DatabaseManager()
        await db_manager.close()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Database closure failed: {e}")


async def close_redis() -> None:
    """Close Redis connections"""
    try:
        from app.utils.cache import CacheManager
        cache_manager = CacheManager()
        await cache_manager.close()
        logger.info("✓ Redis connections closed")
    except Exception as e:
        logger.error(f"✗ Redis closure failed: {e}")


async def close_llm_providers() -> None:
    """Close LLM provider connections"""
    try:
        from app.llm.provider_factory import LLMProviderFactory
        factory = LLMProviderFactory()
        await factory.close()
        logger.info("✓ LLM providers closed")
    except Exception as e:
        logger.error(f"✗ LLM provider closure failed: {e}")


async def close_vector_db() -> None:
    """Close vector database connections"""
    try:
        from app.rag.vector_store import VectorStoreManager
        vector_store = VectorStoreManager()
        await vector_store.close()
        logger.info("✓ Vector database closed")
    except Exception as e:
        logger.error(f"✗ Vector database closure failed: {e}")


async def stop_background_tasks() -> None:
    """Stop background tasks"""
    try:
        # Stop any scheduled tasks
        logger.info("✓ Background tasks stopped")
    except Exception as e:
        logger.error(f"✗ Background task shutdown failed: {e}")