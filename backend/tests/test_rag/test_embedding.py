"""
HealthConnect AI - Embedding Tests
===================================
Tests for EmbeddingGenerator.
"""

import pytest

from app.rag.embedding import EmbeddingGenerator


class TestEmbeddingGenerator:
    """Test embedding generator"""
    
    @pytest.fixture
    def generator(self):
        """Create embedding generator"""
        return EmbeddingGenerator()
    
    def test_initialization(self, generator):
        """Test initialization"""
        assert generator.model_name is not None
        assert generator.dimension > 0
    
    def test_cosine_similarity_same(self, generator):
        """Test cosine similarity of identical vectors"""
        vec = [1.0, 0.0, 0.0]
        similarity = generator.cosine_similarity(vec, vec)
        assert abs(similarity - 1.0) < 0.001
    
    def test_cosine_similarity_orthogonal(self, generator):
        """Test cosine similarity of orthogonal vectors"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = generator.cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 0.001
    
    def test_normalize_embedding(self, generator):
        """Test embedding normalization"""
        vec = [3.0, 4.0, 0.0]
        normalized = generator.normalize_embedding(vec)
        
        import numpy as np
        norm = np.linalg.norm(normalized)
        assert abs(norm - 1.0) < 0.001