"""
HealthConnect AI - API Package
===============================
FastAPI API endpoints and routing.

Structure:
- v1: API version 1
  - endpoints: Individual endpoint modules
  - router: Main API router
"""

from app.api.v1.router import api_router

__all__ = ["api_router"]