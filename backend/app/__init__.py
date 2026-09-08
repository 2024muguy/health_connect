"""
HealthConnect AI Assistant - Main Application Package
======================================================
Production-grade conversational AI for healthcare administrative support.

This package contains:
- FastAPI application
- Multi-agent orchestration system
- RAG pipeline
- MCP tool integration
- Database models
- API endpoints

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "HealthConnect AI Team"

from app.main import create_app

__all__ = ["create_app", "__version__"]