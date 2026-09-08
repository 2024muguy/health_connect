"""
HealthConnect AI - Data Preparation
====================================
Prepare training data from raw sources.

Features:
- Knowledge Base processing
- Training data generation
- Data augmentation
- Train/validation split
- Data validation
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

from config.logging_config import get_logger

logger = get_logger(__name__)


class DataPreparation:
    """
    Data preparation for model training.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DataPreparation initialized with data_dir={data_dir}")
    
    def load_knowledge_base(self, file_path: Optional[str] = None) -> str:
        """
        Load HealthConnect Knowledge Base.
        
        Args:
            file_path: Path to knowledge base file
            
        Returns:
            str: Knowledge base text
        """
        file_path = file_path or str(self.raw_dir / "HealthConnect_Clinic_Knowledge_Base.docx")
        
        if not Path(file_path).exists():
            logger.warning(f"Knowledge base file not found: {file_path}")
            return ""
        
        from app.rag.document_ingestion import DocumentIngestionPipeline
        
        pipeline = DocumentIngestionPipeline()
        text = pipeline._parse_docx(file_path)
        cleaned = pipeline._clean_text(text)
        
        logger.info(f"Loaded knowledge base: {len(cleaned)} characters")
        return cleaned
    
    def generate_intent_training_data(
        self,
        output_file: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Generate intent classification training data.
        
        Args:
            output_file: Output file path
            
        Returns:
            List[Dict]: Training data
        """
        # Define intent examples
        intent_examples = {
            "appointment_booking": [
                "How do I book an appointment?",
                "I need to schedule a visit",
                "Can I make an appointment?",
                "I want to book a consultation",
                "How do I schedule an appointment?",
                "I need to see a doctor",
                "Book me an appointment please",
                "I want to make a booking",
                "Schedule a visit for me",
                "How can I book a time slot?",
            ],
            "appointment_reschedule": [
                "I need to reschedule my appointment",
                "Can I change my appointment time?",
                "I want to move my appointment",
                "Reschedule my booking please",
                "I need to change my visit date",
                "Can I postpone my appointment?",
                "Move my appointment to next week",
                "I need to rebook my appointment",
                "Change my appointment time",
                "I can't make it, can I reschedule?",
            ],
            "appointment_cancel": [
                "I need to cancel my appointment",
                "Cancel my booking please",
                "How do I cancel my appointment?",
                "I want to cancel my visit",
                "Remove my appointment from schedule",
                "I can't come, please cancel",
                "Cancel my appointment for Tuesday",
                "I need to cancel my booking",
                "Delete my appointment please",
                "How can I cancel my visit?",
            ],
            "clinic_information": [
                "Where is HealthConnect Clinic located?",
                "What are your opening hours?",
                "What services do you offer?",
                "Do you have a location downtown?",
                "What's your phone number?",
                "What insurance do you accept?",
                "Tell me about your clinic",
                "What departments do you have?",
                "Where can I find you?",
                "What are your business hours?",
            ],
            "billing_query": [
                "How much does a consultation cost?",
                "What payment methods do you accept?",
                "How do I pay my bill?",
                "What are your fees?",
                "Do you offer payment plans?",
                "How much is a follow-up visit?",
                "What's the cost of a physical?",
                "Can I get an invoice?",
                "How do billing and payments work?",
                "What are your charges?",
            ],
            "insurance_query": [
                "Do you accept Blue Cross?",
                "Is my insurance covered?",
                "What insurance plans do you take?",
                "Are you in-network for Aetna?",
                "Do you accept Medicare?",
                "What's my copay?",
                "Do you take UnitedHealthcare?",
                "Insurance coverage question",
                "Is Cigna accepted here?",
                "Do you work with my insurance?",
            ],
            "preparation_guidance": [
                "What should I bring to my appointment?",
                "How should I prepare for my visit?",
                "Do I need to fast before my test?",
                "What documents do I need?",
                "How early should I arrive?",
                "What should I wear to my appointment?",
                "Preparation instructions please",
                "What do I need for my first visit?",
                "How do I prepare for a blood test?",
                "What should I know before coming?",
            ],
            "policy_query": [
                "What's your cancellation policy?",
                "What happens if I'm late?",
                "Do you charge for no-shows?",
                "What's your late arrival policy?",
                "Do I need a referral?",
                "What's your policy on missed appointments?",
                "How does your waitlist work?",
                "What are your rules?",
                "Tell me about your policies",
                "What's your rescheduling policy?",
            ],
            "medical_advice_request": [
                "I have a headache, what should I take?",
                "Is this rash serious?",
                "Should I be worried about my blood pressure?",
                "What medication should I take for a cold?",
                "Do I need antibiotics?",
                "My stomach hurts, what should I do?",
                "Is my fever too high?",
                "Should I see a doctor for this?",
                "What treatment do you recommend?",
                "Can you diagnose my symptoms?",
            ],
            "emergency": [
                "I'm having chest pain!",
                "I can't breathe!",
                "I'm bleeding severely",
                "I think I'm having a stroke",
                "Call 911!",
                "This is an emergency",
                "I'm dying!",
                "Severe allergic reaction",
                "I'm unconscious",
                "Heart attack symptoms",
            ],
            "escalation_request": [
                "Can I talk to a human?",
                "I want to speak to an agent",
                "Get me a real person",
                "I need human assistance",
                "Transfer me to staff",
                "Can I speak to someone?",
                "I want to talk to a representative",
                "Get me out of this bot",
                "Human please",
                "I need to talk to a person",
            ],
            "feedback": [
                "Thank you for your help",
                "This was very helpful",
                "Great service!",
                "Terrible experience",
                "I'm not satisfied",
                "You were very helpful",
                "This bot is useless",
                "Excellent support",
                "I want to leave a review",
                "Here's my feedback",
            ],
        }
        
        # Generate training data
        training_data = []
        
        for intent, examples in intent_examples.items():
            for example in examples:
                training_data.append({
                    "text": example,
                    "label": intent,
                })
        
        # Save to file
        if output_file:
            output_path = self.processed_dir / output_file
            with open(output_path, 'w') as f:
                json.dump(training_data, f, indent=2)
            logger.info(f"Saved {len(training_data)} intent training examples to {output_path}")
        
        return training_data
    
    def generate_safety_training_data(
        self,
        output_file: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Generate safety classification training data.
        
        Args:
            output_file: Output file path
            
        Returns:
            List[Dict]: Training data
        """
        safety_examples = {
            "safe": [
                "How do I book an appointment?",
                "What are your hours?",
                "Where are you located?",
                "How much does a visit cost?",
                "What insurance do you accept?",
                "What should I bring?",
                "How do I reschedule?",
                "Can I cancel my appointment?",
                "What services do you offer?",
                "How early should I arrive?",
            ],
            "medical_advice_request": [
                "I have a headache, what should I take?",
                "Is this rash serious?",
                "What medication should I take?",
                "Do I need antibiotics for this?",
                "Should I be worried about my symptoms?",
                "What treatment do you recommend?",
                "Can you diagnose my condition?",
                "My fever won't go away, what should I do?",
                "Is my blood pressure too high?",
                "What should I do for my back pain?",
            ],
            "emergency": [
                "I'm having chest pain!",
                "I can't breathe!",
                "I'm bleeding severely!",
                "I think I'm having a stroke!",
                "I'm having a heart attack!",
                "Call 911 now!",
                "I'm dying!",
                "Severe allergic reaction!",
                "I'm unconscious!",
                "Help, emergency!",
            ],
            "prescription_request": [
                "Can you refill my prescription?",
                "I need more medication",
                "Renew my prescription please",
                "Can I get a refill?",
                "I need my medicine refilled",
                "Increase my dosage",
                "Change my medication",
                "I need a new prescription",
                "Can you prescribe something?",
                "My prescription ran out",
            ],
            "test_result_query": [
                "What does my blood test show?",
                "Can you interpret my results?",
                "What does my X-ray show?",
                "Explain my lab results",
                "Is my cholesterol normal?",
                "What does my MRI mean?",
                "Tell me about my test results",
                "Are my results normal?",
                "What did my CT scan show?",
                "Can you read my lab report?",
            ],
            "out_of_scope": [
                "What's the weather like?",
                "Who won the game?",
                "Tell me a joke",
                "What's the news today?",
                "How to cook pasta?",
                "What movies are playing?",
                "What's the stock market doing?",
                "Who's the president?",
                "What's the meaning of life?",
                "Can you sing a song?",
            ],
            "pii_request": [
                "What's my social security number?",
                "Tell me my credit card number",
                "What's my password?",
                "Give me patient information",
                "What's John's medical history?",
                "Show me my bank account",
                "What's my insurance number?",
                "Tell me about another patient",
                "Access someone's records",
                "What's my date of birth on file?",
            ],
            "abusive_language": [
                "You're stupid!",
                "This is terrible service",
                "You're useless",
                "I hate this bot",
                "You're an idiot",
                "Worst experience ever",
                "You're dumb",
                "This is awful",
                "You're worthless",
                "I'm so frustrated with you",
            ],
        }
        
        training_data = []
        
        for category, examples in safety_examples.items():
            for example in examples:
                training_data.append({
                    "text": example,
                    "label": category,
                })
        
        # Save to file
        if output_file:
            output_path = self.processed_dir / output_file
            with open(output_path, 'w') as f:
                json.dump(training_data, f, indent=2)
            logger.info(f"Saved {len(training_data)} safety training examples to {output_path}")
        
        return training_data
    
    def generate_evaluation_queries(
        self,
        output_file: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Generate evaluation queries for testing.
        
        Args:
            output_file: Output file path
            
        Returns:
            List[Dict]: Evaluation queries
        """
        evaluation_queries = [
            # In-scope queries
            {"query": "Where is HealthConnect Clinic located?", "expected_intent": "clinic_information", "difficulty": "easy"},
            {"query": "What are your opening hours?", "expected_intent": "clinic_information", "difficulty": "easy"},
            {"query": "How do I book an appointment?", "expected_intent": "appointment_booking", "difficulty": "easy"},
            {"query": "I need to reschedule my appointment", "expected_intent": "appointment_reschedule", "difficulty": "easy"},
            {"query": "Cancel my appointment please", "expected_intent": "appointment_cancel", "difficulty": "easy"},
            {"query": "What services do you offer?", "expected_intent": "clinic_information", "difficulty": "easy"},
            {"query": "How much does a consultation cost?", "expected_intent": "billing_query", "difficulty": "medium"},
            {"query": "Do you accept my insurance?", "expected_intent": "insurance_query", "difficulty": "medium"},
            {"query": "What should I bring to my appointment?", "expected_intent": "preparation_guidance", "difficulty": "medium"},
            {"query": "What's your cancellation policy?", "expected_intent": "policy_query", "difficulty": "medium"},
            
            # Out-of-scope queries
            {"query": "I have a headache, what should I take?", "expected_intent": "medical_advice_request", "difficulty": "easy"},
            {"query": "I'm having chest pain!", "expected_intent": "emergency", "difficulty": "easy"},
            {"query": "Can you refill my prescription?", "expected_intent": "prescription_request", "difficulty": "medium"},
            {"query": "What does my blood test show?", "expected_intent": "test_result_query", "difficulty": "medium"},
            {"query": "Can I talk to a human?", "expected_intent": "escalation_request", "difficulty": "easy"},
            {"query": "What's the weather like?", "expected_intent": "out_of_scope", "difficulty": "easy"},
            
            # Edge cases
            {"query": "", "expected_intent": "error", "difficulty": "edge"},
            {"query": "Help!", "expected_intent": "emergency_or_escalation", "difficulty": "edge"},
            {"query": "You're a bot", "expected_intent": "feedback", "difficulty": "edge"},
            {"query": "I want to book AND cancel", "expected_intent": "multiple_intents", "difficulty": "hard"},
            {"query": "What's the meaning of life?", "expected_intent": "out_of_scope", "difficulty": "edge"},
        ]
        
        if output_file:
            output_path = self.processed_dir / output_file
            with open(output_path, 'w') as f:
                json.dump(evaluation_queries, f, indent=2)
            logger.info(f"Saved {len(evaluation_queries)} evaluation queries to {output_path}")
        
        return evaluation_queries
    
    def split_data(
        self,
        data: List[Dict[str, Any]],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        shuffle: bool = True,
        seed: int = 42,
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            data: Data to split
            train_ratio: Training ratio
            val_ratio: Validation ratio
            test_ratio: Test ratio
            shuffle: Whether to shuffle
            seed: Random seed
            
        Returns:
            Tuple: (train_data, val_data, test_data)
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001
        
        if shuffle:
            random.seed(seed)
            random.shuffle(data)
        
        total = len(data)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        train_data = data[:train_end]
        val_data = data[train_end:val_end]
        test_data = data[val_end:]
        
        logger.info(
            f"Split data: {len(train_data)} train, "
            f"{len(val_data)} val, {len(test_data)} test"
        )
        
        return train_data, val_data, test_data
    
    def validate_data(
        self,
        data: List[Dict[str, Any]],
        required_fields: List[str] = ["text", "label"],
    ) -> List[Dict[str, Any]]:
        """
        Validate training data.
        
        Args:
            data: Data to validate
            required_fields: Required fields
            
        Returns:
            List: Validated data
        """
        valid_data = []
        
        for item in data:
            is_valid = all(field in item for field in required_fields)
            if is_valid:
                valid_data.append(item)
        
        removed_count = len(data) - len(valid_data)
        if removed_count > 0:
            logger.warning(f"Removed {removed_count} invalid data points")
        
        return valid_data