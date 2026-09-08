"""
HealthConnect AI - Embedding Generator
=======================================
Embedding generation for RAG pipeline.

Features:
- Multiple embedding models
- Batch processing
- Caching
- Normalization
"""

import asyncio
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional
from functools import lru_cache

from app.rag.chunking import Chunk

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingGenerator:
    """
    Embedding generator for text chunks.
    Supports OpenAI, Sentence-Transformers, and local models.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.rag.EMBEDDING_MODEL
        self.dimension = self._get_dimension()
        self._cache: Dict[str, List[float]] = {}
        self._batch_size = 32
        logger.info(f"EmbeddingGenerator initialized with {self.model_name}")
    
    def _get_dimension(self) -> int:
        """Get embedding dimension for model"""
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "BAAI/bge-small-en": 384,
            "BAAI/bge-base-en": 768,
            "BAAI/bge-large-en": 1024,
        }
        return dimensions.get(self.model_name, 1536)
    
    async def embed_chunks(
        self,
        chunks: List[Chunk],
        batch_size: Optional[int] = None,
    ) -> List[Chunk]:
        """
        Generate embeddings for chunks.
        
        Args:
            chunks: List of chunks
            batch_size: Batch size for processing
            
        Returns:
            List[Chunk]: Chunks with embeddings
        """
        batch_size = batch_size or self._batch_size
        
        # Filter chunks that already have embeddings
        chunks_to_embed = [c for c in chunks if c.embedding is None]
        chunks_with_embedding = [c for c in chunks if c.embedding is not None]
        
        logger.info(f"Embedding {len(chunks_to_embed)} chunks (batch size: {batch_size})")
        
        # Process in batches
        for i in range(0, len(chunks_to_embed), batch_size):
            batch = chunks_to_embed[i:i + batch_size]
            texts = [chunk.text for chunk in batch]
            
            # Generate embeddings for batch
            embeddings = await self.embed_texts(texts)
            
            # Assign embeddings to chunks
            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding
        
        return chunks_with_embedding + chunks_to_embed
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List[List[float]]: List of embeddings
        """
        # Check cache
        embeddings = []
        texts_to_embed = []
        text_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                embeddings.append(self._cache[cache_key])
            else:
                texts_to_embed.append(text)
                text_indices.append(i)
                embeddings.append(None)  # Placeholder
        
        if texts_to_embed:
            # Generate embeddings for uncached texts
            new_embeddings = await self._generate_embeddings(texts_to_embed)
            
            # Update cache and results
            for text, embedding in zip(texts_to_embed, new_embeddings):
                cache_key = self._get_cache_key(text)
                self._cache[cache_key] = embedding
                idx = text_indices.pop(0)
                embeddings[idx] = embedding
        
        return embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text
            
        Returns:
            List[float]: Query embedding
        """
        embeddings = await self.embed_texts([query])
        return embeddings[0]
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using the configured model.
        
        Args:
            texts: List of texts
            
        Returns:
            List[List[float]]: Embeddings
        """
        # Use OpenAI embeddings
        if self.model_name.startswith("text-embedding"):
            return await self._openai_embeddings(texts)
        
        # Use Sentence-Transformers
        elif self.model_name in ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "BAAI/bge-small-en", "BAAI/bge-base-en", "BAAI/bge-large-en"]:
            return await self._sentence_transformer_embeddings(texts)
        
        else:
            raise ValueError(f"Unsupported embedding model: {self.model_name}")
    
    async def _openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=settings.llm.OPENAI_API_KEY)
        
        try:
            response = await client.embeddings.create(
                model=self.model_name,
                input=texts,
            )
            
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in embeddings]
            
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    async def _sentence_transformer_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Sentence-Transformers"""
        from sentence_transformers import SentenceTransformer
        
        # Load model (cached)
        model = self._get_sentence_transformer_model()
        
        # Run in thread pool (CPU-bound)
        embeddings = await asyncio.to_thread(
            model.encode,
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        
        return embeddings.tolist()
    
    def _get_sentence_transformer_model(self):
        """Get or load Sentence-Transformer model"""
        if not hasattr(self, '_st_model'):
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(self.model_name)
        
        return self._st_model
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return f"{self.model_name}:{hashlib.sha256(text.encode()).hexdigest()}"
    
    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """L2 normalize embedding"""
        arr = np.array(embedding)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr.tolist()
    
    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
    ) -> float:
        """Calculate cosine similarity between embeddings"""
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def clear_cache(self) -> None:
        """Clear embedding cache"""
        self._cache = {}
        logger.info("Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "model": self.model_name,
            "cache_size": len(self._cache),
            "dimension": self.dimension,
        }