#!/usr/bin/env python
"""
HealthConnect AI - No-Show Predictor Training Script
=====================================================
Trains the no-show prediction model.

Usage:
    python scripts/train_no_show_predictor.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from training.no_show_predictor import NoShowPredictor, main
from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)

if __name__ == "__main__":
    main()
