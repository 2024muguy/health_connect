#!/usr/bin/env python
"""
HealthConnect AI - Knowledge Base Ingestion Script
===================================================
Ingest HealthConnect Knowledge Base into vector store.

Usage:
    python scripts/ingest_knowledge_base.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.document_ingestion import DocumentIngestionPipeline
from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)


async def main():
    """Main ingestion function"""
    logger.info("Starting Knowledge Base ingestion...")
    
    pipeline = DocumentIngestionPipeline()
    
    # Ingest knowledge base
    kb_path = Path("data/raw/HealthConnect_Clinic_Knowledge_Base.docx")
    
    if not kb_path.exists():
        logger.error(f"Knowledge Base file not found: {kb_path}")
        sys.exit(1)
    
    result = await pipeline.ingest_knowledge_base(str(kb_path))
    
    logger.info(f"Ingestion complete: {result}")
    return result


if __name__ == "__main__":
    asyncio.run(main())