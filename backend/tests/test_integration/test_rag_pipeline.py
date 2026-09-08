"""
HealthConnect AI - RAG Pipeline Integration Tests
==================================================
End-to-end RAG pipeline tests.
"""

import pytest

from app.rag.chunking import ChunkingEngine
from app.rag.embedding import EmbeddingGenerator
from app.rag.context_builder import ContextBuilder
from app.rag.citation_generator import CitationGenerator
from app.rag.retriever import RetrievalResult


class TestRAGPipeline:
    """Test complete RAG pipeline"""
    
    @pytest.fixture
    def chunking_engine(self):
        return ChunkingEngine()
    
    @pytest.fixture
    def embedding_generator(self):
        return EmbeddingGenerator()
    
    @pytest.fixture
    def context_builder(self):
        return ContextBuilder()
    
    @pytest.fixture
    def citation_generator(self):
        return CitationGenerator()
    
    def test_document_to_chunks(self, chunking_engine):
        """Test document chunking"""
        text = "This is a test document for RAG pipeline. " * 50
        chunks = chunking_engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=50,
            overlap=10,
        )
        
        assert len(chunks) > 0
    
    def test_context_building(self, context_builder):
        """Test context building from results"""
        results = [
            RetrievalResult(
                chunk_id="chunk_1",
                text="HealthConnect Clinic is located at 123 Main Street.",
                score=0.9,
                retrieval_method="vector",
            ),
            RetrievalResult(
                chunk_id="chunk_2",
                text="Opening hours: Monday-Friday 8am-6pm.",
                score=0.85,
                retrieval_method="vector",
            ),
        ]
        
        context = context_builder.build_context(results)
        assert context.chunks_used == 2
        assert len(context.context_text) > 0
        assert len(context.sources) == 2
    
    def test_citation_generation(self, citation_generator):
        """Test citation generation"""
        sources = [
            {"index": 1, "chunk_id": "chunk_1", "document_id": "doc_1"},
            {"index": 2, "chunk_id": "chunk_2", "document_id": "doc_1"},
        ]
        
        citations = citation_generator.generate_citations(sources)
        assert len(citations) == 2
        assert citations[0]["index"] == "1"
        assert citations[0]["chunk_id"] == "chunk_1"