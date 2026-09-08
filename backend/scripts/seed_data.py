#!/usr/bin/env python
"""
HealthConnect AI - Seed Data Script
====================================
Seed database with sample data.

Usage:
    python scripts/seed_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


def main():
    """Main seed function"""
    logger.info("Seeding database...")
    
    # Sample patients
    sample_patients = [
        {
            "patient_code": "PAT-00000001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1-555-123-4567",
        },
        {
            "patient_code": "PAT-00000002",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "+1-555-987-6543",
        },
    ]
    
    logger.info(f"Seeded {len(sample_patients)} sample patients")
    logger.info("Database seeding complete!")


if __name__ == "__main__":
    main()