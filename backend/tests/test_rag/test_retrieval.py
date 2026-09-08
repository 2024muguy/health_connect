"""
HealthConnect AI - Retrieval Tests
===================================
Tests for HybridRetriever.
"""

import pytest

from app.rag.retriever import HybridRetriever, RetrievalResult


class TestHybridRetriever:
    """Test hybrid retriever"""
    
    @pytest.fixture
    def retriever(self):
        """Create retriever"""
        return HybridRetriever()
    
    def test_tokenize_query(self, retriever):
        """Test query tokenization"""
        tokens = retriever._tokenize_query("How do I book an appointment?")
        assert "book" in tokens
        assert "appointment" in tokens
        assert "how" not in tokens  # Stopword removed
    
    def test_empty_query(self, retriever):
        """Test empty query"""
        tokens = retriever._tokenize_query("")
        assert tokens == []
    
    def test_retrieval_result_to_dict(self):
        """Test retrieval result conversion"""
        result = RetrievalResult(
            chunk_id="chunk_1",
            text="Test text",
            score=0.85,
            retrieval_method="vector",
        )
        
        result_dict = result.to_dict()
        assert result_dict["chunk_id"] == "chunk_1"
        assert result_dict["score"] == 0.85
        assert result_dict["retrieval_method"] == "vector"