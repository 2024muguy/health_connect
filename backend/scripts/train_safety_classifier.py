#!/usr/bin/env python
"""
HealthConnect AI - Safety Classifier Training Script
=====================================================
Train safety classification model.

Usage:
    python scripts/train_safety_classifier.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from training.data_preparation import DataPreparation
from training.safety_classifier import SafetyClassifierTrainer
from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


def main():
    """Main training function"""
    logger.info("Starting safety classifier training...")
    
    # Prepare data
    data_prep = DataPreparation()
    training_data = data_prep.generate_safety_training_data()
    
    # Split data
    train_data, val_data, test_data = data_prep.split_data(
        training_data,
        train_ratio=0.8,
        val_ratio=0.1,
        test_ratio=0.1,
    )
    
    logger.info(f"Training: {len(train_data)}, Validation: {len(val_data)}, Test: {len(test_data)}")
    
    # Train model
    trainer = SafetyClassifierTrainer()
    results = trainer.train(train_data, val_data)
    
    logger.info(f"Training results: {results}")
    
    # Save model
    trainer.save()
    
    logger.info("Safety classifier training complete!")


if __name__ == "__main__":
    main()