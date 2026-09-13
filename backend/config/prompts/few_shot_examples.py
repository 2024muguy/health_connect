


"""
HealthConnect AI - Few-Shot Examples
# =====================================
Few-shot examples for training and in-context learning.

Categories:
- Intent classification examples
- Safety classification examples
- Response generation examples
"""

from typing import List, Dict, Any

# ============================================
# INTENT CLASSIFICATION EXAMPLES
# ============================================
INTENT_CLASSIFICATION_EXAMPLES: List[Dict[str, Any]] = [
    {
        "input": "How do I book an appointment?",
        "output": {
            "intent": "appointment_booking",
            "confidence": 0.95,
            "routing": "appointment_service"
        }
    },
    {
        "input": "I need to change my appointment to next week",
        "output": {
            "intent": "appointment_reschedule",
            "confidence": 0.93,
            "routing": "appointment_service"
        }
    },
    {
        "input": "Cancel my appointment for Tuesday",
        "output": {
            "intent": "appointment_cancel",
            "confidence": 0.94,
            "routing": "appointment_service"
        }
    },
    {
        "input": "Where is your clinic located?",
        "output": {
            "intent": "clinic_information",
            "confidence": 0.96,
            "routing": "knowledge_base"
        }
    },
    {
        "input": "How much does a consultation cost?",
        "output": {
            "intent": "billing_query",
            "confidence": 0.92,
            "routing": "billing_service"
        }
    },
    {
        "input": "Do you accept Blue Cross insurance?",
        "output": {
            "intent": "insurance_query",
            "confidence": 0.94,
            "routing": "insurance_service"
        }
    },
    {
        "input": "What should I bring to my appointment?",
        "output": {
            "intent": "preparation_guidance",
            "confidence": 0.91,
            "routing": "knowledge_base"
        }
    },
    {
        "input": "What's your late arrival policy?",
        "output": {
            "intent": "policy_query",
            "confidence": 0.93,
            "routing": "knowledge_base"
        }
    },
    {
        "input": "I have a headache, what should I take?",
        "output": {
            "intent": "medical_advice_request",
            "confidence": 0.97,
            "routing": "safety_protocol"
        }
    },
    {
        "input": "I'm having chest pain!",
        "output": {
            "intent": "emergency",
            "confidence": 0.99,
            "routing": "emergency_protocol"
        }
    },
    {
        "input": "Can I talk to a human?",
        "output": {
            "intent": "escalation_request",
            "confidence": 0.95,
            "routing": "escalation_service"
        }
    },
    {
        "input": "What's the weather like today?",
        "output": {
            "intent": "out_of_scope",
            "confidence": 0.98,
            "routing": "redirect_service"
        }
    },
]

# ============================================
# SAFETY CLASSIFICATION EXAMPLES
# ============================================
SAFETY_CLASSIFICATION_EXAMPLES: List[Dict[str, Any]] = [
    {
        "input": "How do I book an appointment?",
        "output": {
            "safety_category": "safe",
            "action": "allow",
            "confidence": 0.98,
            "risk_score": 5
        }
    },
    {
        "input": "What are your opening hours?",
        "output": {
            "safety_category": "safe",
            "action": "allow",
            "confidence": 0.97,
            "risk_score": 3
        }
    },
    {
        "input": "I have a rash, is it serious?",
        "output": {
            "safety_category": "medical_advice_request",
            "action": "block",
            "confidence": 0.95,
            "risk_score": 70
        }
    },
    {
        "input": "Can you refill my prescription?",
        "output": {
            "safety_category": "prescription_request",
            "action": "escalate",
            "confidence": 0.96,
            "risk_score": 60
        }
    },
    {
        "input": "What does my blood test show?",
        "output": {
            "safety_category": "test_result_query",
            "action": "escalate",
            "confidence": 0.94,
            "risk_score": 65
        }
    },
    {
        "input": "I'm having severe chest pain!",
        "output": {
            "safety_category": "emergency",
            "action": "emergency_protocol",
            "confidence": 0.99,
            "risk_score": 100
        }
    },
    {
        "input": "What's my social security number on file?",
        "output": {
            "safety_category": "pii_request",
            "action": "block",
            "confidence": 0.93,
            "risk_score": 75
        }
    },
    {
        "input": "You're a stupid bot!",
        "output": {
            "safety_category": "abusive_language",
            "action": "block",
            "confidence": 0.97,
            "risk_score": 50
        }
    },
]

# ============================================
# RESPONSE GENERATION EXAMPLES
# ============================================
RESPONSE_EXAMPLES: List[Dict[str, Any]] = [
    {
        "context": "HealthConnect Clinic is located at 123 Main Street. Opening hours are Monday-Friday 8am-6pm.",
        "query": "Where are you located?",
        "response": "HealthConnect Clinic is located at 123 Main Street. Our opening hours are Monday through Friday from 8:00 AM to 6:00 PM."
    },
    {
        "context": "To cancel an appointment, please call at least 24 hours in advance. There is no fee for cancellations made within this timeframe.",
        "query": "How do I cancel my appointment?",
        "response": "To cancel your appointment, please contact us at least 24 hours in advance. There is no cancellation fee if you cancel within this timeframe. Would you like me to help you with the cancellation process?"
    },
    {
        "context": "Please bring your insurance card, photo ID, and a list of current medications to your appointment.",
        "query": "What should I bring?",
        "response": "For your appointment, please bring: 1) Your insurance card, 2) A valid photo ID, and 3) A list of your current medications. Is there anything else you'd like to know?"
    },
]

# ============================================
# ALL FEW-SHOT EXAMPLES
# ============================================
FEW_SHOT_EXAMPLES: Dict[str, List[Dict[str, Any]]] = {
    "intent_classification": INTENT_CLASSIFICATION_EXAMPLES,
    "safety_classification": SAFETY_CLASSIFICATION_EXAMPLES,
    "response_generation": RESPONSE_EXAMPLES,
}