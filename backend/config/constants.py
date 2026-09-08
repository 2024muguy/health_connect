"""
HealthConnect AI - Global Constants
====================================
Centralized constants for the entire application.

Categories:
- Application metadata
- Intent classification
- Safety categories
- Escalation tiers
- RAG pipeline constants
- API constants
- Error messages
"""

# ============================================
# APPLICATION METADATA
# ============================================
APP_NAME = "HealthConnect AI Assistant"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Production-grade conversational AI for healthcare administrative support"
API_PREFIX = "/api/v1"

# ============================================
# ENVIRONMENT
# ============================================
class Environment:
    """Environment constants"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


# ============================================
# INTENT CLASSIFICATION
# ============================================
INTENT_LABELS = [
    "appointment_booking",
    "appointment_reschedule",
    "appointment_cancel",
    "clinic_information",
    "billing_query",
    "insurance_query",
    "preparation_guidance",
    "policy_query",
    "general_faq",
    "medical_advice_request",
    "emergency",
    "feedback",
    "escalation_request",
    "out_of_scope",
]

INTENT_ROUTING_MAP = {
    "appointment_booking": "appointment_service",
    "appointment_reschedule": "appointment_service",
    "appointment_cancel": "appointment_service",
    "clinic_information": "knowledge_base",
    "billing_query": "billing_service",
    "insurance_query": "insurance_service",
    "preparation_guidance": "knowledge_base",
    "policy_query": "knowledge_base",
    "general_faq": "knowledge_base",
    "medical_advice_request": "safety_protocol",
    "emergency": "emergency_protocol",
    "feedback": "feedback_service",
    "escalation_request": "escalation_service",
    "out_of_scope": "redirect_service",
}

# ============================================
# SAFETY CATEGORIES
# ============================================
SAFETY_CATEGORIES = [
    "safe",
    "medical_advice_request",
    "emergency",
    "prescription_request",
    "test_result_query",
    "out_of_scope",
    "pii_request",
    "abusive_language",
]

SAFETY_ACTIONS = {
    "safe": "allow",
    "medical_advice_request": "block",
    "emergency": "emergency_protocol",
    "prescription_request": "escalate",
    "test_result_query": "escalate",
    "out_of_scope": "redirect",
    "pii_request": "block",
    "abusive_language": "block",
}

SAFETY_SEVERITY = {
    "safe": 0,
    "out_of_scope": 1,
    "pii_request": 3,
    "prescription_request": 4,
    "test_result_query": 4,
    "medical_advice_request": 4,
    "abusive_language": 4,
    "emergency": 5,
}

# ============================================
# ESCALATION TIERS
# ============================================
ESCALATION_TIERS = {
    0: {
        "name": "AI Resolution",
        "description": "Assistant fully resolves query",
        "response_time": "< 2 seconds",
        "handler": "ai_agent",
    },
    1: {
        "name": "Guided Self-Service",
        "description": "Assistant provides instructions for self-resolution",
        "response_time": "< 2 seconds",
        "handler": "ai_agent",
    },
    2: {
        "name": "Action Escalation",
        "description": "Request requires human action",
        "response_time": "< 5 minutes",
        "handler": "scheduling_staff",
    },
    3: {
        "name": "Knowledge Escalation",
        "description": "Query in-scope but not in Knowledge Base",
        "response_time": "< 1 hour",
        "handler": "department_staff",
    },
    4: {
        "name": "Safety Escalation",
        "description": "Medical or safety concern detected",
        "response_time": "Immediate",
        "handler": "clinical_staff",
    },
    5: {
        "name": "Emergency Protocol",
        "description": "Medical emergency indicated",
        "response_time": "Immediate",
        "handler": "emergency_services",
    },
}

# ============================================
# RAG PIPELINE CONSTANTS
# ============================================
RAG_DEFAULTS = {
    "CHUNK_SIZE": 512,
    "CHUNK_OVERLAP": 77,
    "TOP_K_RETRIEVAL": 5,
    "EMBEDDING_MODEL": "text-embedding-3-small",
    "EMBEDDING_DIMENSION": 1536,
    "RERANKER_MODEL": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "MAX_CONTEXT_LENGTH": 4096,
    "HYBRID_SEARCH_ALPHA": 0.6,
    "RRF_CONSTANT": 60,
}

# ============================================
# LLM PROVIDERS
# ============================================
LLM_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "default_model": "gpt-4",
        "embedding_model": "text-embedding-3-small",
        "max_tokens": 2048,
    },
    "anthropic": {
        "name": "Anthropic",
        "default_model": "claude-3-opus-20240229",
        "embedding_model": None,
        "max_tokens": 2048,
    },
    "google": {
        "name": "Google Gemini",
        "default_model": "gemini-pro",
        "embedding_model": "embedding-001",
        "max_tokens": 2048,
    },
}

# ============================================
# API CONSTANTS
# ============================================
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "ACCEPTED": 202,
    "NO_CONTENT": 204,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    "TOO_MANY_REQUESTS": 429,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
}

# ============================================
# ERROR MESSAGES
# ============================================
ERROR_MESSAGES = {
    "AUTHENTICATION_REQUIRED": "Authentication is required for this endpoint",
    "INVALID_CREDENTIALS": "Invalid username or password",
    "TOKEN_EXPIRED": "Authentication token has expired",
    "TOKEN_INVALID": "Invalid authentication token",
    "PERMISSION_DENIED": "You do not have permission to perform this action",
    "RESOURCE_NOT_FOUND": "The requested resource was not found",
    "VALIDATION_ERROR": "Request validation failed",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded. Please try again later",
    "INTERNAL_ERROR": "An internal server error occurred",
    "SERVICE_UNAVAILABLE": "Service is temporarily unavailable",
    "SAFETY_BLOCK": "This request was blocked by our safety system",
    "EMERGENCY_DETECTED": "Medical emergency detected. Please call 911 immediately",
}

# ============================================
# SAFETY MESSAGES
# ============================================
SAFETY_MESSAGES = {
    "medical_advice": (
        "I apologize, but I'm not able to provide medical advice. "
        "For medical questions, please contact your healthcare provider directly. "
        "Would you like me to help you with appointment scheduling or other administrative tasks?"
    ),
    "emergency": (
        "IMPORTANT: If you are experiencing a medical emergency, please call 911 "
        "(or your local emergency number) immediately. Do not wait for a response from this assistant."
    ),
    "prescription": (
        "I'm not able to process prescription requests. "
        "Please contact your pharmacy or healthcare provider directly for prescription-related matters."
    ),
    "test_results": (
        "I cannot interpret test results. "
        "Please contact your ordering physician to discuss your test results."
    ),
    "out_of_scope": (
        "I apologize, but that request is outside my scope of support. "
        "I can help with appointment scheduling, clinic information, billing questions, "
        "and other administrative tasks. Would you like help with any of these?"
    ),
}

# ============================================
# MCP TOOL CONSTANTS
# ============================================
MCP_SERVER_TYPES = [
    "database",
    "calendar",
    "email",
    "knowledge_base",
    "analytics",
    "notification",
]

MCP_TOOL_CATEGORIES = {
    "database": ["query", "insert", "update", "delete", "schema"],
    "calendar": ["schedule", "reschedule", "cancel", "availability"],
    "email": ["send", "template", "track"],
    "knowledge_base": ["search", "retrieve", "index"],
    "analytics": ["track", "report", "dashboard"],
    "notification": ["sms", "push", "reminder"],
}

# ============================================
# CACHE CONSTANTS
# ============================================
CACHE_TTL = {
    "clinic_info": 3600,          # 1 hour
    "faq": 7200,                   # 2 hours
    "embedding": 86400,            # 24 hours
    "conversation": 1800,          # 30 minutes
    "user_session": 86400,         # 24 hours
    "rate_limit": 60,              # 1 minute
}

CACHE_PREFIX = {
    "clinic": "clinic:",
    "faq": "faq:",
    "embedding": "embedding:",
    "conversation": "conv:",
    "session": "session:",
    "rate_limit": "rate:",
}

# ============================================
# TIME CONSTANTS
# ============================================
TIME_CONSTANTS = {
    "SECOND": 1,
    "MINUTE": 60,
    "HOUR": 3600,
    "DAY": 86400,
    "WEEK": 604800,
    "MONTH": 2592000,
}