#!/usr/bin/env python
"""
HealthConnect AI - Model Evaluation Script
===========================================
Evaluate all trained models.

Usage:
    python scripts/evaluate_models.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from training.data_preparation import DataPreparation
from training.intent_classifier import IntentClassifierTrainer
from training.safety_classifier import SafetyClassifierTrainer
from training.evaluator import ModelEvaluator
from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


def main():
    """Main evaluation function"""
    logger.info("Starting model evaluation...")
    
    data_prep = DataPreparation()
    evaluator = ModelEvaluator()
    
    # Evaluate intent classifier
    logger.info("Evaluating intent classifier...")
    intent_trainer = IntentClassifierTrainer()
    intent_trainer.load()
    
    intent_test = data_prep.generate_intent_training_data()[:20]
    intent_predictions = []
    intent_true = []
    
    for item in intent_test:
        prediction = intent_trainer.predict(item["text"])
        intent_predictions.append(prediction["intent"])
        intent_true.append(item["label"])
    
    intent_labels = list(set(intent_true))
    intent_results = evaluator.evaluate_classifier(
        y_true=[intent_labels.index(l) for l in intent_true],
        y_pred=[intent_labels.index(l) if l in intent_labels else 0 for l in intent_predictions],
        labels=intent_labels,
    )
    
    logger.info(f"Intent classifier results: Accuracy={intent_results['accuracy']:.4f}")
    
    # Evaluate safety classifier
    logger.info("Evaluating safety classifier...")
    safety_trainer = SafetyClassifierTrainer()
    safety_trainer.load()
    
    safety_test = data_prep.generate_safety_training_data()[:20]
    safety_predictions = []
    safety_true = []
    
    for item in safety_test:
        prediction = safety_trainer.predict(item["text"])
        safety_predictions.append(prediction["safety_category"])
        safety_true.append(item["label"])
    
    safety_labels = list(set(safety_true))
    safety_results = evaluator.evaluate_classifier(
        y_true=[safety_labels.index(l) for l in safety_true],
        y_pred=[safety_labels.index(l) if l in safety_labels else 0 for l in safety_predictions],
        labels=safety_labels,
    )
    
    logger.info(f"Safety classifier results: Accuracy={safety_results['accuracy']:.4f}")
    
    logger.info("Model evaluation complete!")


if __name__ == "__main__":
    main()