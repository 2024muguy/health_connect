#!/usr/bin/env python
"""
HealthConnect AI - Database Setup Script
=========================================
Initialize database tables.

Usage:
    python scripts/setup_db.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.session import init_db
from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


async def main():
    """Main setup function"""
    logger.info("Setting up database...")
    
    await init_db()
    
    logger.info("Database setup complete!")


if __name__ == "__main__":
    asyncio.run(main())