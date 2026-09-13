#!/usr/bin/env python
"""
HealthConnect AI - Complete Data Ingestion Script
===================================================
Ingests ALL HealthConnect data files into the vector store:

1. HealthConnect_Clinic_Knowledge_Base.docx - Primary knowledge source
2. HealthConnect_Appointment_Data.csv - Appointment records for analysis
3. HealthConnect_Data_Dictionary.xlsx - Column definitions

Usage:
    python scripts/ingest_knowledge_base.py
"""

import asyncio
import sys
import json
import aiohttp
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_settings
from config.logging_config import setup_logging, get_logger

setup_logging(log_level="INFO", environment="development")
logger = get_logger(__name__)
settings = get_settings()

OLLAMA_URL = "http://localhost:11434"


async def generate_ollama_embedding(text: str) -> List[float]:
    """Generate embedding using Ollama nomic-embed-text."""
    payload = {"model": "nomic-embed-text", "prompt": text[:5000]}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_URL}/api/embeddings",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("embedding", [])
                return []
    except Exception as e:
        logger.warning(f"Embedding failed: {e}")
        return []


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    step = chunk_size - overlap
    chunks = []
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())
    return chunks


async def ingest_knowledge_base_docx() -> Dict[str, Any]:
    """Ingest the Knowledge Base DOCX file."""
    kb_path = Path("data/raw/HealthConnect_Clinic_Knowledge_Base.docx")
    
    if not kb_path.exists():
        logger.warning(f"Knowledge Base not found: {kb_path}")
        return {"status": "skipped", "reason": "file_not_found"}
    
    logger.info(f"\n{'='*60}")
    logger.info("1. INGESTING: HealthConnect_Clinic_Knowledge_Base.docx")
    logger.info(f"{'='*60}")
    
    from app.rag.document_ingestion import DocumentIngestionPipeline
    pipeline = DocumentIngestionPipeline()
    
    # Parse document
    text = pipeline._parse_docx(str(kb_path))
    logger.info(f"Parsed {len(text)} characters")
    
    cleaned = pipeline._clean_text(text)
    logger.info(f"Cleaned to {len(cleaned)} characters")
    
    # Create chunks
    chunks = chunk_text(cleaned)
    logger.info(f"Created {len(chunks)} chunks")
    
    # Generate embeddings
    data = []
    for i, chunk in enumerate(chunks):
        embedding = await generate_ollama_embedding(chunk)
        if embedding:
            data.append({
                "id": f"kb_{i}",
                "source": "knowledge_base",
                "text": chunk,
                "embedding": embedding,
                "metadata": {"document": "HealthConnect_Clinic_Knowledge_Base.docx", "chunk": i}
            })
        
        if (i + 1) % 5 == 0:
            logger.info(f"  Embedded {i + 1}/{len(chunks)} chunks")
    
    logger.info(f"✅ Knowledge Base: {len(data)} chunks indexed")
    return {"status": "completed", "chunks": len(data), "data": data}


async def ingest_appointment_data_csv() -> Dict[str, Any]:
    """Ingest the Appointment Data CSV file."""
    csv_path = Path("data/raw/HealthConnect_Appointment_Data.csv")
    
    if not csv_path.exists():
        logger.warning(f"Appointment data not found: {csv_path}")
        return {"status": "skipped", "reason": "file_not_found"}
    
    logger.info(f"\n{'='*60}")
    logger.info("2. INGESTING: HealthConnect_Appointment_Data.csv")
    logger.info(f"{'='*60}")
    
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} records")
    
    # Create summary texts
    texts = []
    
    # Overview
    texts.append(f"HealthConnect Clinic appointment dataset: {len(df)} records. Columns: {', '.join(df.columns.tolist())}.")
    
    # Outcome statistics
    if 'appointment_outcome' in df.columns:
        outcome = df['appointment_outcome'].value_counts()
        texts.append(f"Appointment outcomes: {outcome.to_dict()}")
    
    # Key metrics
    metrics = {
        'distance_to_clinic_km': 'Average distance',
        'waiting_time_minutes': 'Average waiting time',
        'booking_lead_days': 'Average booking lead time',
        'previous_no_shows': 'Average previous no-shows',
    }
    
    for col, label in metrics.items():
        if col in df.columns:
            texts.append(f"{label}: {df[col].mean():.2f}")
    
    # Appointment types
    if 'appointment_type' in df.columns:
        types = df['appointment_type'].value_counts().head(5)
        texts.append(f"Appointment types: {types.to_dict()}")
    
    # Demographics
    if 'age_group' in df.columns:
        ages = df['age_group'].value_counts()
        texts.append(f"Age groups: {ages.to_dict()}")
    
    # Generate embeddings
    data = []
    for i, text in enumerate(texts):
        embedding = await generate_ollama_embedding(text)
        if embedding:
            data.append({
                "id": f"appt_{i}",
                "source": "appointment_data",
                "text": text,
                "embedding": embedding,
                "metadata": {"document": "HealthConnect_Appointment_Data.csv"}
            })
    
    logger.info(f"✅ Appointment Data: {len(data)} summaries indexed")
    return {"status": "completed", "chunks": len(data), "data": data}


async def ingest_data_dictionary_xlsx() -> Dict[str, Any]:
    """Ingest the Data Dictionary XLSX file."""
    xlsx_path = Path("data/raw/HealthConnect_Data_Dictionary.xlsx")
    
    if not xlsx_path.exists():
        logger.warning(f"Data dictionary not found: {xlsx_path}")
        return {"status": "skipped", "reason": "file_not_found"}
    
    logger.info(f"\n{'='*60}")
    logger.info("3. INGESTING: HealthConnect_Data_Dictionary.xlsx")
    logger.info(f"{'='*60}")
    
    try:
        xlsx = pd.ExcelFile(xlsx_path)
        logger.info(f"Sheets: {xlsx.sheet_names}")
        
        texts = []
        for sheet in xlsx.sheet_names:
            df = pd.read_excel(xlsx_path, sheet_name=sheet)
            texts.append(f"Sheet '{sheet}': columns: {', '.join(df.columns.tolist())}")
            
            for _, row in df.iterrows():
                row_text = " | ".join(f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col]))
                if len(row_text) > 20:
                    texts.append(row_text)
        
        # Generate embeddings
        data = []
        for i, text in enumerate(texts):
            embedding = await generate_ollama_embedding(text)
            if embedding:
                data.append({
                    "id": f"dict_{i}",
                    "source": "data_dictionary",
                    "text": text,
                    "embedding": embedding,
                    "metadata": {"document": "HealthConnect_Data_Dictionary.xlsx"}
                })
            
            if (i + 1) % 10 == 0:
                logger.info(f"  Embedded {i + 1}/{len(texts)} entries")
        
        logger.info(f"✅ Data Dictionary: {len(data)} entries indexed")
        return {"status": "completed", "chunks": len(data), "data": data}
        
    except Exception as e:
        logger.warning(f"XLSX processing failed: {e}")
        return {"status": "failed", "reason": str(e)}


async def main():
    """Main ingestion function for ALL data files."""
    logger.info("=" * 60)
    logger.info("HealthConnect AI - Complete Data Ingestion")
    logger.info("=" * 60)
    
    # Show configuration
    logger.info(f"Embedding model: nomic-embed-text (Ollama)")
    logger.info(f"Groq API key: {'Configured ✅' if settings.groq.API_KEY else 'NOT SET ❌'}")
    logger.info(f"Ollama: {'Available' if settings.ollama.BASE_URL else 'Not set'}")
    
    # Test embedding first
    logger.info("\n--- Testing Embedding Generation ---")
    test_embedding = await generate_ollama_embedding("Test embedding")
    if test_embedding:
        logger.info(f"✅ Embedding works! Dimension: {len(test_embedding)}")
    else:
        logger.error("❌ Embedding failed. Is Ollama running?")
        sys.exit(1)
    
    # Ingest all three files
    all_data = []
    results = {}
    
    # 1. Knowledge Base DOCX
    result = await ingest_knowledge_base_docx()
    results["knowledge_base"] = {"status": result["status"], "chunks": result.get("chunks", 0)}
    all_data.extend(result.get("data", []))
    
    # 2. Appointment Data CSV
    result = await ingest_appointment_data_csv()
    results["appointment_data"] = {"status": result["status"], "chunks": result.get("chunks", 0)}
    all_data.extend(result.get("data", []))
    
    # 3. Data Dictionary XLSX
    result = await ingest_data_dictionary_xlsx()
    results["data_dictionary"] = {"status": result["status"], "chunks": result.get("chunks", 0)}
    all_data.extend(result.get("data", []))
    
    # Save to JSON
    output_file = Path("data/processed/rag_knowledge_base.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    logger.info(f"\n✅ Saved {len(all_data)} items to {output_file}")
    
    # Build FAISS index
    logger.info("\n--- Building FAISS Index ---")
    
    try:
        import numpy as np
        import faiss
        
        embeddings = np.array([item["embedding"] for item in all_data if item["embedding"]], dtype=np.float32)
        
        if len(embeddings) > 0:
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            
            faiss.write_index(index, str(Path("data/processed/faiss_index.bin")))
            logger.info(f"✅ FAISS index: {index.ntotal} vectors, {dimension} dims")
        else:
            logger.warning("No embeddings to index")
            
    except Exception as e:
        logger.warning(f"FAISS indexing failed: {e}")
    
    # Summary
    sources = {}
    for item in all_data:
        src = item.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    
    logger.info("\n" + "=" * 60)
    logger.info("INGESTION COMPLETE!")
    logger.info("=" * 60)
    for src, count in sources.items():
        logger.info(f"  {src}: {count} items")
    logger.info(f"  Total: {len(all_data)} items")
    
    # Save results
    results_path = Path("data/processed/ingestion_results.json")
    with open(results_path, 'w') as f:
        json.dump({
            "results": results,
            "total_items": len(all_data),
            "sources": sources,
        }, f, indent=2, default=str)
    
    logger.info(f"Results saved to: {results_path}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
