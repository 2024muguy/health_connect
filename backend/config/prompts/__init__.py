"""
HealthConnect AI - Prompt Templates Package
============================================
Prompt templates for all AI agents in the system.

This package provides:
- System prompts for each agent
- Few-shot examples for training
- Reusable prompt templates

Usage:
    from config.prompts.system_prompts import SYSTEM_PROMPTS
    from config.prompts.few_shot_examples import FEW_SHOT_EXAMPLES
    from config.prompts.prompt_templates import PromptTemplate
"""

from config.prompts.system_prompts import (
    SYSTEM_PROMPTS,
    CONVERSATION_AGENT_PROMPT,
    SAFETY_AGENT_PROMPT,
    INTENT_ROUTER_PROMPT,
    KNOWLEDGE_AGENT_PROMPT,
)
from config.prompts.few_shot_examples import (
    FEW_SHOT_EXAMPLES,
    INTENT_CLASSIFICATION_EXAMPLES,
    SAFETY_CLASSIFICATION_EXAMPLES,
)
from config.prompts.prompt_templates import (
    PromptTemplate,
    RAGPromptTemplate,
    SafetyPromptTemplate,
    IntentPromptTemplate,
)

__all__ = [
    "SYSTEM_PROMPTS",
    "CONVERSATION_AGENT_PROMPT",
    "SAFETY_AGENT_PROMPT",
    "INTENT_ROUTER_PROMPT",
    "KNOWLEDGE_AGENT_PROMPT",
    "FEW_SHOT_EXAMPLES",
    "INTENT_CLASSIFICATION_EXAMPLES",
    "SAFETY_CLASSIFICATION_EXAMPLES",
    "PromptTemplate",
    "RAGPromptTemplate",
    "SafetyPromptTemplate",
    "IntentPromptTemplate",
]