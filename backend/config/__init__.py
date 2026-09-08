"""
HealthConnect AI - Configuration Package
=========================================
Central configuration management for the HealthConnect AI Assistant.

This package provides:
- Application settings via environment variables
- Logging configuration
- Global constants
- Prompt templates for AI agents

Usage:
    from config import settings
    from config import constants
    from config.logging_config import setup_logging
"""

from config.settings import Settings, get_settings
from config.constants import (
    APP_NAME,
    APP_VERSION,
    ENVIRONMENT,
    SAFETY_CATEGORIES,
    INTENT_LABELS,
    ESCALATION_TIERS,
)

__all__ = [
    "Settings",
    "get_settings",
    "APP_NAME",
    "APP_VERSION",
    "ENVIRONMENT",
    "SAFETY_CATEGORIES",
    "INTENT_LABELS",
    "ESCALATION_TIERS",
]