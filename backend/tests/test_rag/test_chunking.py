"""
HealthConnect AI - Chunking Tests
==================================
Tests for ChunkingEngine.
"""

import pytest

from app.rag.chunking import ChunkingEngine, ChunkingStrategy


class TestChunkingEngine:
    """Test chunking engine"""
    
    @pytest.fixture
    def engine(self):
        """Create chunking engine"""
        return ChunkingEngine()
    
    def test_fixed_size_chunking(self, engine):
        """Test fixed-size chunking"""
        text = "This is a sample text that will be chunked into smaller pieces based on the specified chunk size."
        
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=20,
            overlap=0,
            strategy=ChunkingStrategy.FIXED_SIZE,
        )
        
        assert len(chunks) > 0
        assert all(chunk.text for chunk in chunks)
        assert all(chunk.document_id == "test_doc" for chunk in chunks)
        assert all(chunk.token_count <= 20 for chunk in chunks)
    
    def test_sentence_aware_chunking(self, engine):
        """Test sentence-aware chunking"""
        text = "This is the first sentence. This is the second sentence. This is the third sentence."
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=50,
            overlap=10,
            strategy=ChunkingStrategy.SENTENCE_AWARE,
        )
        
        assert len(chunks) > 0
        assert all(chunk.text for chunk in chunks)
    
    def test_semantic_chunking(self, engine):
        """Test semantic chunking"""
        text = """Paragraph one with some content.
        
        Paragraph two with different content.
        
        Paragraph three with more content."""
        
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=100,
            overlap=20,
            strategy=ChunkingStrategy.SEMANTIC,
        )
        
        assert len(chunks) > 0
        assert all(chunk.text for chunk in chunks)
    
    def test_hybrid_chunking(self, engine):
        """Test hybrid chunking"""
        text = "This is a test document. It contains multiple sentences. " * 10
        
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=150,
            overlap=25,
            strategy=ChunkingStrategy.HYBRID,
        )
        
        assert len(chunks) > 0
        assert all(chunk.text for chunk in chunks)
        assert all(chunk.document_id == "test_doc" for chunk in chunks)
    
    def test_empty_text(self, engine):
        """Test chunking empty text"""
        chunks = engine.chunk_document(
            "",
            document_id="test_doc",
            chunk_size=100,
            overlap=10,
            strategy=ChunkingStrategy.FIXED_SIZE,
        )
        
        assert len(chunks) == 0
    
    def test_text_smaller_than_chunk_size(self, engine):
        """Test chunking text smaller than chunk size"""
        text = "Small text"
        
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=100,
            overlap=10,
            strategy=ChunkingStrategy.FIXED_SIZE,
        )
        
        assert len(chunks) == 1
        assert chunks[0].text == text
    
    def test_overlap_between_chunks(self, engine):
        """Test overlap between consecutive chunks"""
        text = "word " * 100  # Create text with repeating pattern
        
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=20,
            overlap=5,
            strategy=ChunkingStrategy.FIXED_SIZE,
        )
        
        assert len(chunks) > 1
        
        # Check that consecutive chunks have overlapping content
        if len(chunks) > 1:
            first_chunk_words = set(chunks[0].text.split())
            second_chunk_words = set(chunks[1].text.split())
            overlap_words = first_chunk_words & second_chunk_words
            assert len(overlap_words) > 0
    
    def test_chunk_metadata(self, engine):
        """Test chunk metadata"""
        text = "Test document content for metadata testing."
        
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=50,
            overlap=5,
            strategy=ChunkingStrategy.FIXED_SIZE,
        )
        
        assert len(chunks) > 0
        assert hasattr(chunks[0], 'text')
        assert hasattr(chunks[0], 'document_id')
        assert hasattr(chunks[0], 'chunk_id')
        assert hasattr(chunks[0], 'token_count')
        assert hasattr(chunks[0], 'metadata')
    
    def test_token_count_accuracy(self, engine):
        """Test token count accuracy"""
        text = "This is a test sentence with exactly ten words in it."
        
        chunks = engine.chunk_document(
            text,
            document_id="test_doc",
            chunk_size=100,
            overlap=0,
            strategy=ChunkingStrategy.FIXED_SIZE,
        )
        
        assert len(chunks) == 1
        # Token count should be approximately the number of words
        expected_tokens = len(text.split())
        assert abs(chunks[0].token_count - expected_tokens) <= 2