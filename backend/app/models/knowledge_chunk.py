"""
HealthConnect AI - Knowledge Chunk Model
=========================================
Knowledge chunk database model for RAG pipeline.

Fields:
- Chunk content and metadata
- Document source
- Embedding reference
- Version tracking
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    Text,
    Float,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, SoftDeleteMixin


class KnowledgeChunk(BaseModel, SoftDeleteMixin):
    """
    Knowledge chunk model for RAG pipeline.
    """
    
    __tablename__ = "knowledge_chunks"
    
    # ============================================
    # Chunk Identification
    # ============================================
    chunk_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique chunk code",
    )
    
    document_id = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Source document identifier",
    )
    
    # ============================================
    # Chunk Content
    # ============================================
    content = Column(
        Text,
        nullable=False,
        comment="Chunk text content",
    )
    
    chunk_index = Column(
        Integer,
        nullable=False,
        comment="Position of chunk in document",
    )
    
    token_count = Column(
        Integer,
        nullable=False,
        comment="Number of tokens in chunk",
    )
    
    # ============================================
    # Embedding Information
    # ============================================
    embedding_model = Column(
        String(100),
        nullable=True,
        comment="Embedding model used",
    )
    
    embedding_dimension = Column(
        Integer,
        nullable=True,
        comment="Embedding vector dimension",
    )
    
    embedding_ref = Column(
        String(255),
        nullable=True,
        comment="Reference to vector in Pinecone",
    )
    
    # ============================================
    # Metadata
    # ============================================
    section = Column(
        String(255),
        nullable=True,
        comment="Document section",
    )
    
    title = Column(
        String(500),
        nullable=True,
        comment="Document title",
    )
    
    model_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional metadata",
    )
    
    # ============================================
    # Version Tracking
    # ============================================
    version = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Chunk version",
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether chunk is active",
    )
    
    # ============================================
    # Usage Statistics
    # ============================================
    retrieval_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times retrieved",
    )
    
    citation_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times cited",
    )
    
    last_retrieved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last retrieval timestamp",
    )
    
    # ============================================
    # Quality Metrics
    # ============================================
    relevance_score = Column(
        Float,
        nullable=True,
        comment="Average relevance score from user feedback",
    )
    
    quality_score = Column(
        Float,
        nullable=True,
        comment="Quality score from evaluations",
    )
    
    # ============================================
    # Indexes
    # ============================================
    __table_args__ = (
        Index("idx_chunk_document", "document_id"),
        Index("idx_chunk_active", "is_active"),
        Index("idx_chunk_embedding_ref", "embedding_ref"),
        UniqueConstraint("document_id", "chunk_index", name="uq_chunk_doc_index"),
    )
    
    @property
    def is_indexed(self) -> bool:
        """Check if chunk has been indexed in vector database"""
        return bool(self.embedding_ref)
    
    def increment_retrieval(self) -> None:
        """Increment retrieval count"""
        self.retrieval_count += 1
        self.last_retrieved_at = datetime.now(timezone.utc)
    
    def increment_citation(self) -> None:
        """Increment citation count"""
        self.citation_count += 1