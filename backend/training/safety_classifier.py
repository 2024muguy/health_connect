"""
HealthConnect AI - Safety Classifier Trainer
=============================================
Train safety classification model.

Features:
- Safety model training
- Risk scoring
- Model evaluation
- Model saving
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

from config.logging_config import get_logger

logger = get_logger(__name__)


class SafetyClassifierTrainer:
    """
    Safety classifier trainer.
    """
    
    def __init__(self, model_dir: str = "data/models/safety_classifier"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.vectorizer = None
        self.classifier = None
        self.label_mapping = {}
        
        # Risk scores for each category
        self.risk_scores = {
            "safe": 0,
            "out_of_scope": 10,
            "abusive_language": 50,
            "prescription_request": 60,
            "test_result_query": 65,
            "pii_request": 70,
            "medical_advice_request": 80,
            "emergency": 100,
        }
        
        logger.info(f"SafetyClassifierTrainer initialized with model_dir={model_dir}")
    
    def train(
        self,
        train_data: List[Dict[str, str]],
        val_data: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Train safety classifier.
        
        Args:
            train_data: Training data
            val_data: Validation data
            
        Returns:
            Dict: Training results
        """
        texts = [item["text"] for item in train_data]
        labels = [item["label"] for item in train_data]
        
        # Create label mapping from TRAINING data only
        unique_labels = sorted(set(labels))
        self.label_mapping = {label: i for i, label in enumerate(unique_labels)}
        
        y = [self.label_mapping[label] for label in labels]
        
        # Vectorize
        self.vectorizer = TfidfVectorizer(
            max_features=3000,
            ngram_range=(1, 2),
            stop_words='english',
        )
        X = self.vectorizer.fit_transform(texts)
        
        # Train classifier
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
        )
        self.classifier.fit(X, y)
        
        logger.info(f"Trained safety classifier on {len(texts)} examples")
        
        # Evaluate
        train_pred = self.classifier.predict(X)
        train_accuracy = accuracy_score(y, train_pred)
        
        results = {
            "train_accuracy": train_accuracy,
            "num_classes": len(unique_labels),
            "num_examples": len(texts),
            "labels": unique_labels,
        }
        
        if val_data:
            val_texts = [item["text"] for item in val_data]
            val_labels = [item["label"] for item in val_data]
            
            # Filter validation labels to only those seen in training
            valid_indices = [
                i for i, label in enumerate(val_labels)
                if label in self.label_mapping
            ]
            
            val_texts_filtered = [val_texts[i] for i in valid_indices]
            val_labels_filtered = [val_labels[i] for i in valid_indices]
            
            if val_texts_filtered:
                val_y = [self.label_mapping[label] for label in val_labels_filtered]
                
                val_X = self.vectorizer.transform(val_texts_filtered)
                val_pred = self.classifier.predict(val_X)
                
                val_accuracy = accuracy_score(val_y, val_pred)
                results["val_accuracy"] = val_accuracy
                
                val_unique_labels = sorted(set(val_labels_filtered))
                
                report = classification_report(
                    val_y,
                    val_pred,
                    labels=[self.label_mapping[l] for l in val_unique_labels],
                    target_names=val_unique_labels,
                    output_dict=True,
                    zero_division=0,
                )
                results["classification_report"] = report
                logger.info(f"Validation accuracy: {val_accuracy:.4f}")
            else:
                results["val_accuracy"] = 0.0
                logger.warning("No validation samples with known labels")
        
        return results
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict safety category for text.
        
        Args:
            text: Input text
            
        Returns:
            Dict: Prediction result
        """
        if not self.classifier or not self.vectorizer:
            raise RuntimeError("Model not trained")
        
        X = self.vectorizer.transform([text])
        prediction = self.classifier.predict(X)[0]
        
        reverse_mapping = {i: label for label, i in self.label_mapping.items()}
        category = reverse_mapping.get(prediction, "safe")
        
        # Get probability
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = float(max(probabilities))
        
        # Get risk score
        risk_score = self.risk_scores.get(category, 50)
        
        return {
            "safety_category": category,
            "confidence": confidence,
            "risk_score": risk_score,
            "action": self._determine_action(category, risk_score),
        }
    
    def _determine_action(self, category: str, risk_score: int) -> str:
        """Determine action based on category and risk score"""
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
    
    def save(self) -> None:
        """Save model"""
        import joblib
        
        joblib.dump(self.vectorizer, self.model_dir / "vectorizer.pkl")
        joblib.dump(self.classifier, self.model_dir / "classifier.pkl")
        
        with open(self.model_dir / "label_mapping.json", 'w') as f:
            json.dump(self.label_mapping, f, indent=2)
        
        with open(self.model_dir / "risk_scores.json", 'w') as f:
            json.dump(self.risk_scores, f, indent=2)
        
        logger.info(f"Saved safety model to {self.model_dir}")
    
    def load(self) -> None:
        """Load model"""
        import joblib
        
        self.vectorizer = joblib.load(self.model_dir / "vectorizer.pkl")
        self.classifier = joblib.load(self.model_dir / "classifier.pkl")
        
        with open(self.model_dir / "label_mapping.json", 'r') as f:
            self.label_mapping = json.load(f)
        
        logger.info(f"Loaded safety model from {self.model_dir}")
