"""
HealthConnect AI - Configuration Package
=========================================
Central configuration management for the HealthConnect AI Assistant.

This package provides:
- Application settings via environment variables
- Logging configuration
- Global constants
- Prompt templates for AI agents
"""

from config.settings import Settings, get_settings
from config.constants import (
    APP_NAME,
    APP_VERSION,
    SAFETY_CATEGORIES,
    INTENT_LABELS,
    ESCALATION_TIERS,
)

__all__ = [
    "Settings",
    "get_settings",
    "APP_NAME",
    "APP_VERSION",
    "SAFETY_CATEGORIES",
    "INTENT_LABELS",
    "ESCALATION_TIERS",
]
