"""
HealthConnect AI - Document Ingestion Pipeline
===============================================
Complete document processing pipeline for RAG.

Stages:
1. Document parsing (DOCX, PDF, HTML, TXT)
2. Text cleaning and normalization
3. Metadata extraction
4. Chunking
5. Embedding generation
6. Vector indexing
"""

import os
import re
import hashlib
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from app.rag.chunking import ChunkingEngine
from app.rag.embedding import EmbeddingGenerator
from app.rag.vector_store import VectorStoreManager

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DocumentFormat(Enum):
    """Supported document formats"""
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"
    CSV = "csv"
    JSON = "json"


class DocumentStatus(Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PARSING = "parsing"
    CLEANING = "cleaning"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentIngestionPipeline:
    """
    Complete document ingestion pipeline.
    Handles all stages from raw document to indexed chunks.
    """
    
    def __init__(self):
        self.chunking_engine = ChunkingEngine()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStoreManager()
        self.supported_formats = {
            ".docx": DocumentFormat.DOCX,
            ".pdf": DocumentFormat.PDF,
            ".html": DocumentFormat.HTML,
            ".htm": DocumentFormat.HTML,
            ".txt": DocumentFormat.TXT,
            ".csv": DocumentFormat.CSV,
            ".json": DocumentFormat.JSON,
        }
    
    async def ingest_file(
        self,
        file_path: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a document file.
        
        Args:
            file_path: Path to document
            document_id: Optional document ID
            metadata: Additional metadata
            
        Returns:
            Dict: Ingestion result
        """
        start_time = datetime.now(timezone.utc)
        
        # Validate file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine format
        file_extension = file_path.suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        document_format = self.supported_formats[file_extension]
        
        # Generate document ID if not provided
        if not document_id:
            file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            document_id = f"doc_{file_hash[:16]}"
        
        logger.info(f"Ingesting document: {file_path} (ID: {document_id})")
        
        try:
            # Stage 1: Parse
            raw_text = await self._parse_document(file_path, document_format)
            logger.info(f"Parsed {len(raw_text)} characters")
            
            # Stage 2: Clean
            cleaned_text = self._clean_text(raw_text)
            logger.info(f"Cleaned to {len(cleaned_text)} characters")
            
            # Stage 3: Chunk
            chunks = self.chunking_engine.chunk_document(
                cleaned_text,
                document_id=document_id,
                chunk_size=settings.rag.CHUNK_SIZE,
                overlap=settings.rag.CHUNK_OVERLAP,
            )
            logger.info(f"Created {len(chunks)} chunks")
            
            # Stage 4: Embed
            chunks = await self.embedding_generator.embed_chunks(chunks)
            logger.info(f"Generated embeddings for {len(chunks)} chunks")
            
            # Stage 5: Index
            indexed_count = await self.vector_store.upsert_chunks(chunks)
            logger.info(f"Indexed {indexed_count} chunks")
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return {
                "document_id": document_id,
                "status": DocumentStatus.COMPLETED.value,
                "chunks_created": len(chunks),
                "chunks_indexed": indexed_count,
                "processing_time_seconds": processing_time,
                "metadata": metadata or {},
            }
            
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            raise
    
    async def ingest_knowledge_base(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest the HealthConnect Knowledge Base.
        
        Args:
            file_path: Path to knowledge base document
            
        Returns:
            Dict: Ingestion result
        """
        metadata = {
            "source": "healthconnect_knowledge_base",
            "version": "1.0",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        
        return await self.ingest_file(
            file_path,
            document_id="healthconnect_kb_v1",
            metadata=metadata,
        )
    
    async def refresh_index(self) -> Dict[str, Any]:
        """
        Refresh the vector index.
        Re-ingests the knowledge base.
        """
        kb_path = Path("data/raw/HealthConnect_Clinic_Knowledge_Base.docx")
        
        if not kb_path.exists():
            logger.warning("Knowledge base file not found")
            return {"status": "skipped", "reason": "file_not_found"}
        
        return await self.ingest_knowledge_base(str(kb_path))
    
    async def _parse_document(
        self,
        file_path: Path,
        document_format: DocumentFormat,
    ) -> str:
        """
        Parse document to text.
        
        Args:
            file_path: Document path
            document_format: Document format
            
        Returns:
            str: Parsed text
        """
        parsers = {
            DocumentFormat.DOCX: self._parse_docx,
            DocumentFormat.PDF: self._parse_pdf,
            DocumentFormat.HTML: self._parse_html,
            DocumentFormat.TXT: self._parse_txt,
            DocumentFormat.CSV: self._parse_csv,
            DocumentFormat.JSON: self._parse_json,
        }
        
        parser = parsers.get(document_format)
        if not parser:
            raise ValueError(f"No parser for format: {document_format}")
        
        # Run parser in thread pool (CPU-bound)
        return await asyncio.to_thread(parser, str(file_path))
    
    def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX file"""
        from docx import Document
        
        doc = Document(file_path)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        # Include tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text for cell in row.cells)
                if row_text.strip():
                    text_parts.append(row_text)
        
        return "\n\n".join(text_parts)
    
    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF file"""
        import pdfplumber
        
        text_parts = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def _parse_html(self, file_path: str) -> str:
        """Parse HTML file"""
        from bs4 import BeautifulSoup
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style
        for script in soup(["script", "style"]):
            script.decompose()
        
        return soup.get_text(separator='\n', strip=True)
    
    def _parse_txt(self, file_path: str) -> str:
        """Parse text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_csv(self, file_path: str) -> str:
        """Parse CSV file"""
        import csv
        
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(" | ".join(f"{k}: {v}" for k, v in row.items()))
        
        return "\n".join(rows)
    
    def _parse_json(self, file_path: str) -> str:
        """Parse JSON file"""
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return json.dumps(data, indent=2)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            str: Cleaned text
        """
        import unicodedata
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        # Normalize quotes
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('\u201c', '"').replace('\u201d', '"')
        
        # Normalize dashes
        text = text.replace('\u2013', '-').replace('\u2014', '-')
        
        # Remove extra whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip whitespace per line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text.strip()