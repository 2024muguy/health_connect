"""
HealthConnect AI - Intent Classifier Trainer
=============================================
Train intent classification model.

Features:
- Model training
- Hyperparameter tuning
- Model evaluation
- Model saving
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from config.logging_config import get_logger

logger = get_logger(__name__)


class IntentClassifierTrainer:
    """
    Intent classifier trainer.
    """
    
    def __init__(self, model_dir: str = "data/models/intent_classifier"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.vectorizer = None
        self.classifier = None
        self.label_mapping = {}
        
        logger.info(f"IntentClassifierTrainer initialized with model_dir={model_dir}")
    
    def train(
        self,
        train_data: List[Dict[str, str]],
        val_data: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Train intent classifier.
        
        Args:
            train_data: Training data
            val_data: Validation data
            
        Returns:
            Dict: Training results
        """
        # Prepare data
        texts = [item["text"] for item in train_data]
        labels = [item["label"] for item in train_data]
        
        # Create label mapping
        unique_labels = sorted(set(labels))
        self.label_mapping = {label: i for i, label in enumerate(unique_labels)}
        reverse_mapping = {i: label for label, i in self.label_mapping.items()}
        
        # Encode labels
        y = [self.label_mapping[label] for label in labels]
        
        # Vectorize text
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english',
            sublinear_tf=True,
        )
        X = self.vectorizer.fit_transform(texts)
        
        # Train classifier
        self.classifier = LinearSVC(
            C=1.0,
            class_weight='balanced',
            max_iter=1000,
        )
        self.classifier.fit(X, y)
        
        logger.info(f"Trained intent classifier on {len(texts)} examples")
        
        # Evaluate on training data
        train_pred = self.classifier.predict(X)
        train_accuracy = accuracy_score(y, train_pred)
        
        results = {
            "train_accuracy": train_accuracy,
            "num_classes": len(unique_labels),
            "num_examples": len(texts),
            "labels": unique_labels,
        }
        
        # Evaluate on validation data if provided
        if val_data:
            val_texts = [item["text"] for item in val_data]
            val_labels = [item["label"] for item in val_data]
            val_y = [self.label_mapping.get(label, -1) for label in val_labels]
            
            val_X = self.vectorizer.transform(val_texts)
            val_pred = self.classifier.predict(val_X)
            
            val_accuracy = accuracy_score(val_y, val_pred)
            results["val_accuracy"] = val_accuracy
            
            report = classification_report(val_y, val_pred, target_names=unique_labels, output_dict=True)
            results["classification_report"] = report
        
        return results
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict intent for text.
        
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
        intent = reverse_mapping[prediction]
        
        # Get confidence scores
        if hasattr(self.classifier, 'decision_function'):
            scores = self.classifier.decision_function(X)[0]
            confidence = float(max(scores) - min(scores)) if len(scores) > 1 else 1.0
        else:
            confidence = 1.0
        
        return {
            "intent": intent,
            "confidence": confidence,
        }
    
    def save(self) -> None:
        """Save model"""
        import joblib
        
        joblib.dump(self.vectorizer, self.model_dir / "vectorizer.pkl")
        joblib.dump(self.classifier, self.model_dir / "classifier.pkl")
        
        with open(self.model_dir / "label_mapping.json", 'w') as f:
            json.dump(self.label_mapping, f, indent=2)
        
        logger.info(f"Saved model to {self.model_dir}")
    
    def load(self) -> None:
        """Load model"""
        import joblib
        
        self.vectorizer = joblib.load(self.model_dir / "vectorizer.pkl")
        self.classifier = joblib.load(self.model_dir / "classifier.pkl")
        
        with open(self.model_dir / "label_mapping.json", 'r') as f:
            self.label_mapping = json.load(f)
        
        logger.info(f"Loaded model from {self.model_dir}")