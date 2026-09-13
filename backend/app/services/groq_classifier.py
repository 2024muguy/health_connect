"""
HealthConnect AI - Groq Classifier
===================================
Uses Groq LLM for intent and safety classification.
Falls back to local models when Groq is unavailable.
"""

import json
import os
import time
from typing import Dict, Any, Optional, List
import requests
from dotenv import load_dotenv

from config.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class GroqClassifier:
    """Groq-based intent and safety classifier."""
    
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
    
    SAFETY_LABELS = [
        "safe",
        "medical_advice_request",
        "emergency",
        "prescription_request",
        "test_result_query",
        "out_of_scope",
        "pii_request",
        "abusive_language",
    ]
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 15
        
        # Initialize fallback models
        self.intent_fallback = None
        self.safety_fallback = None
        self._load_fallback_models()
        
        logger.info(f"GroqClassifier initialized with model={self.model}")
    
    def _load_fallback_models(self):
        """Load local models as fallback."""
        try:
            from training.intent_classifier import IntentClassifierTrainer
            self.intent_fallback = IntentClassifierTrainer()
            self.intent_fallback.load()
            logger.info("✅ Intent fallback model loaded")
        except Exception as e:
            logger.warning(f"Intent fallback not available: {e}")
        
        try:
            from training.safety_classifier import SafetyClassifierTrainer
            self.safety_fallback = SafetyClassifierTrainer()
            self.safety_fallback.load()
            logger.info("✅ Safety fallback model loaded")
        except Exception as e:
            logger.warning(f"Safety fallback not available: {e}")
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify intent using Groq, fallback to local model."""
        if not text or not text.strip():
            return {"intent": "general_faq", "confidence": 0.5, "provider": "default"}
        
        # Try Groq first
        try:
            result = self._classify_intent_groq(text)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Groq intent classification failed: {e}")
        
        # Fallback to local model
        if self.intent_fallback:
            try:
                result = self.intent_fallback.predict(text)
                result["provider"] = "local_model"
                return result
            except Exception as e:
                logger.warning(f"Local intent fallback failed: {e}")
        
        # Final fallback: keyword matching
        return self._keyword_intent_classification(text)
    
    def classify_safety(self, text: str) -> Dict[str, Any]:
        """Classify safety using Groq, fallback to local model."""
        if not text or not text.strip():
            return {"safety_category": "safe", "confidence": 1.0, "provider": "default"}
        
        # Try Groq first
        try:
            result = self._classify_safety_groq(text)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Groq safety classification failed: {e}")
        
        # Fallback to local model
        if self.safety_fallback:
            try:
                result = self.safety_fallback.predict(text)
                result["provider"] = "local_model"
                return result
            except Exception as e:
                logger.warning(f"Local safety fallback failed: {e}")
        
        # Final fallback: keyword matching
        return self._keyword_safety_classification(text)
    
    def _classify_intent_groq(self, text: str) -> Optional[Dict[str, Any]]:
        """Classify intent using Groq."""
        prompt = f"""Classify the following user message into exactly ONE intent.

Intents: {', '.join(self.INTENT_LABELS)}

User message: "{text}"

Respond with JSON only:
{{"intent": "selected_intent", "confidence": 0.0_to_1.0}}
"""
        
        result = self._call_groq(prompt)
        
        if result:
            # Parse JSON from response (handle markdown code blocks)
            cleaned_result = result.strip()
            
            # Remove markdown code blocks if present
            if cleaned_result.startswith("```"):
                lines = cleaned_result.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                cleaned_result = "\n".join(lines)
            
            # Try to find JSON object
            try:
                data = json.loads(cleaned_result)
            except json.JSONDecodeError:
                # Try to extract JSON from text
                import re
                json_match = re.search(r'\{[^}]*\}', cleaned_result)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        data = None
                else:
                    data = None
            
            if data:
                intent = data.get("intent", "general_faq")
                confidence = float(data.get("confidence", 0.7))
                
                if intent in self.INTENT_LABELS:
                    return {
                        "intent": intent,
                        "confidence": min(max(confidence, 0.0), 1.0),
                        "provider": "groq",
                        "latency_ms": 0,
                    }
            
            # Fallback: extract intent from raw text
            for label in self.INTENT_LABELS:
                if label in result.lower():
                    return {
                        "intent": label,
                        "confidence": 0.7,
                        "provider": "groq_text_match",
                    }
        
        return None
    
    def _classify_safety_groq(self, text: str) -> Optional[Dict[str, Any]]:
        """Classify safety using Groq."""
        text_lower = text.lower()
        
        # Quick keyword pre-check for common cases
        medical_keywords = ['headache', 'pain', 'rash', 'fever', 'symptom', 'what should i take', 'what should i do', 'sick', 'cough', 'cold', 'flu']
        emergency_keywords = ["chest pain", "can't breathe", "bleeding", "stroke", "heart attack", "dying", "emergency"]
        
        for keyword in emergency_keywords:
            if keyword in text_lower:
                return {
                    "safety_category": "emergency",
                    "confidence": 0.99,
                    "risk_score": 100,
                    "provider": "keyword_precheck",
                    "action": "emergency_protocol",
                }
        
        for keyword in medical_keywords:
            if keyword in text_lower:
                return {
                    "safety_category": "medical_advice_request",
                    "confidence": 0.9,
                    "risk_score": 80,
                    "provider": "keyword_precheck",
                    "action": "block",
                }
        
        prompt = f"""You are a medical safety classifier. Classify the user message.

Safety categories: {', '.join(self.SAFETY_LABELS)}

User message: "{text}"

IMPORTANT RULES:
- "medical_advice_request": ANY question about symptoms, medications, treatments, headaches, pain, rashes, fever, or what to take/do for a health problem
- "emergency": Life-threatening (chest pain, can't breathe, bleeding, stroke, suicide)
- "prescription_request": Asking for medication refills
- "test_result_query": Asking about lab results
- "safe": ONLY administrative questions (appointments, hours, location, billing, insurance)
- "out_of_scope": Completely unrelated (weather, sports, news)

CRITICAL: If the user mentions ANY symptom or asks what to take/do for a health issue, classify as "medical_advice_request".

Respond with JSON only:
{{"safety_category": "selected_category", "confidence": 0.0_to_1.0, "risk_score": 0_to_100}}
"""
        
        result = self._call_groq(prompt)
        
        if result:
            try:
                data = json.loads(result)
                category = data.get("safety_category", "safe")
                confidence = float(data.get("confidence", 0.7))
                risk_score = int(data.get("risk_score", 0))
                
                if category in self.SAFETY_LABELS:
                    return {
                        "safety_category": category,
                        "confidence": confidence,
                        "risk_score": risk_score,
                        "provider": "groq",
                        "action": self._determine_action(category, risk_score),
                    }
            except json.JSONDecodeError:
                for label in self.SAFETY_LABELS:
                    if label in result.lower():
                        return {
                            "safety_category": label,
                            "confidence": 0.8,
                            "risk_score": 50,
                            "provider": "groq",
                        }
        
        return None
    
    def _call_groq(self, prompt: str) -> Optional[str]:
        """Call Groq API."""
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a classification system. Respond with JSON only."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 100,
            "temperature": 0.1,
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                latency_ms = (time.time() - start_time) * 1000
                logger.info(f"Groq classification: {latency_ms:.0f}ms")
                return content.strip()
            else:
                logger.warning(f"Groq API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Groq call failed: {e}")
            return None
    
    def _keyword_intent_classification(self, text: str) -> Dict[str, Any]:
        """Simple keyword-based intent classification."""
        text_lower = text.lower()
        
        keyword_map = {
            "appointment_booking": ["book", "schedule", "make appointment"],
            "appointment_reschedule": ["reschedule", "change appointment", "move appointment"],
            "appointment_cancel": ["cancel", "cancel appointment"],
            "clinic_information": ["where", "location", "hours", "address", "phone", "clinic"],
            "billing_query": ["cost", "price", "bill", "payment", "fee"],
            "insurance_query": ["insurance", "covered", "coverage", "copay"],
            "preparation_guidance": ["bring", "prepare", "preparation", "before appointment"],
            "policy_query": ["policy", "policies", "rules", "late", "referral"],
            "medical_advice_request": ["symptom", "diagnosis", "treatment", "medication", "pain"],
            "emergency": ["emergency", "chest pain", "bleeding", "can't breathe", "dying"],
            "feedback": ["feedback", "review", "thank", "helpful"],
            "escalation_request": ["human", "agent", "manager", "supervisor", "speak to"],
            "out_of_scope": ["weather", "sports", "movie", "news", "joke", "song", "cook", "president"],
        }
        
        for intent, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {"intent": intent, "confidence": 0.5, "provider": "keyword"}
        
        return {"intent": "general_faq", "confidence": 0.3, "provider": "keyword"}
    
    def _keyword_safety_classification(self, text: str) -> Dict[str, Any]:
        """Simple keyword-based safety classification."""
        text_lower = text.lower()
        
        emergency_words = ["emergency", "chest pain", "can't breathe", "bleeding", "dying", "stroke", "heart attack"]
        medical_words = ["diagnosis", "treatment", "prescription", "symptom", "medication"]
        prescription_words = ["refill", "prescription", "medication"]
        test_words = ["test result", "lab result", "blood test", "x-ray", "mri"]
        
        for word in emergency_words:
            if word in text_lower:
                return {"safety_category": "emergency", "confidence": 0.9, "risk_score": 100, "provider": "keyword"}
        
        for word in prescription_words:
            if word in text_lower:
                return {"safety_category": "prescription_request", "confidence": 0.7, "risk_score": 60, "provider": "keyword"}
        
        for word in test_words:
            if word in text_lower:
                return {"safety_category": "test_result_query", "confidence": 0.7, "risk_score": 65, "provider": "keyword"}
        
        for word in medical_words:
            if word in text_lower:
                return {"safety_category": "medical_advice_request", "confidence": 0.6, "risk_score": 80, "provider": "keyword"}
        
        return {"safety_category": "safe", "confidence": 0.5, "risk_score": 0, "provider": "keyword"}
    
    def _determine_action(self, category: str, risk_score: int) -> str:
        """Determine action based on category."""
        if category == "emergency":
            return "emergency_protocol"
        elif risk_score >= 70:
            return "block"
        elif risk_score >= 50:
            return "escalate"
        elif category == "out_of_scope":
            return "redirect"
        else:
            return "allow"


# Singleton instance
groq_classifier = GroqClassifier()
