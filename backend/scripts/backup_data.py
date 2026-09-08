#!/usr/bin/env python
"""
HealthConnect AI - Data Backup Script
======================================
Backup data to archive.

Usage:
    python scripts/backup_data.py
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


def main():
    """Main backup function"""
    logger.info("Starting data backup...")
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup data directory
    data_dir = Path("data")
    if data_dir.exists():
        shutil.copytree(data_dir, backup_dir / "data", dirs_exist_ok=True)
        logger.info(f"Backed up data to {backup_dir / 'data'}")
    
    # Backup logs
    logs_dir = Path("logs")
    if logs_dir.exists():
        shutil.copytree(logs_dir, backup_dir / "logs", dirs_exist_ok=True)
        logger.info(f"Backed up logs to {backup_dir / 'logs'}")
    
    logger.info(f"Backup complete: {backup_dir}")


if __name__ == "__main__":
    main()