"""
HealthConnect AI - RAG Pipeline Package
========================================
Retrieval-Augmented Generation pipeline.

Components:
- Document ingestion
- Chunking
- Embedding generation
- Vector storage
- Retrieval
- Re-ranking
- Context building
- Citation generation
"""

from app.rag.document_ingestion import DocumentIngestionPipeline
from app.rag.chunking import ChunkingEngine
from app.rag.embedding import EmbeddingGenerator
from app.rag.vector_store import VectorStoreManager
from app.rag.retriever import HybridRetriever
from app.rag.reranker import CrossEncoderReranker
from app.rag.context_builder import ContextBuilder
from app.rag.citation_generator import CitationGenerator

__all__ = [
    "DocumentIngestionPipeline",
    "ChunkingEngine",
    "EmbeddingGenerator",
    "VectorStoreManager",
    "HybridRetriever",
    "CrossEncoderReranker",
    "ContextBuilder",
    "CitationGenerator",
]