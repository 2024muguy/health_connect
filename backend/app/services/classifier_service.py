"""
HealthConnect AI - Unified Classification Service
=================================================
Combines intent and safety classification with Groq primary.
"""

from typing import Dict, Any
from app.services.groq_classifier import groq_classifier
from config.logging_config import get_logger

logger = get_logger(__name__)


class ClassifierService:
    """Unified classification service."""
    
    def __init__(self):
        self.classifier = groq_classifier
    
    def classify_message(self, text: str) -> Dict[str, Any]:
        """Classify message for both intent and safety."""
        
        # Safety first (more important)
        safety_result = self.classifier.classify_safety(text)
        
        # If emergency, skip intent (it's obvious)
        if safety_result.get("safety_category") == "emergency":
            intent_result = {"intent": "emergency", "confidence": 1.0, "provider": "safety_override"}
        else:
            intent_result = self.classifier.classify_intent(text)
        
        return {
            "intent": intent_result,
            "safety": safety_result,
            "requires_human": safety_result.get("action") in ["escalate", "block", "emergency_protocol"],
        }
    
    def should_block(self, text: str) -> bool:
        """Check if message should be blocked."""
        safety_result = self.classifier.classify_safety(text)
        return safety_result.get("action") in ["block", "emergency_protocol"]
    
    def get_safety_message(self, text: str) -> str:
        """Get appropriate safety message."""
        safety_result = self.classifier.classify_safety(text)
        category = safety_result.get("safety_category", "safe")
        
        messages = {
            "emergency": "If you are experiencing a medical emergency, please call 911 immediately.",
            "medical_advice_request": "I cannot provide medical advice. Please contact your healthcare provider.",
            "prescription_request": "I cannot process prescription requests. Please contact your pharmacy.",
            "test_result_query": "I cannot interpret test results. Please contact your physician.",
            "pii_request": "I cannot access personal information through this chat.",
            "abusive_language": "Please communicate respectfully so I can better assist you.",
        }
        
        return messages.get(category, "")


# Singleton instance
classifier_service = ClassifierService()
