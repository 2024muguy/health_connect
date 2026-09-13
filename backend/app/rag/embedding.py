"""
HealthConnect AI - Embedding Generator
=======================================
Embedding generation for RAG pipeline.

Supports: Ollama (local), Groq, OpenAI, Sentence-Transformers (local fallback)
"""

import asyncio
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingGenerator:
    """Embedding generator supporting multiple providers."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.rag.EMBEDDING_MODEL
        self.dimension = self._get_dimension()
        self._cache: Dict[str, List[float]] = {}
        self._batch_size = 16
        self._st_model = None
        logger.info(f"EmbeddingGenerator initialized with {self.model_name}")
    
    def _get_dimension(self) -> int:
        """Get embedding dimension for model."""
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "BAAI/bge-small-en": 384,
            "BAAI/bge-base-en": 768,
            "nomic-embed-text": 768,
            "llama3.1": 4096,
            "llama-3.1-8b-instant": 4096,
            "mxbai-embed-large": 1024,
        }
        return dimensions.get(self.model_name, 384)
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query string."""
        embeddings = await self.embed_texts([query])
        return embeddings[0] if embeddings else []
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = []
        texts_to_embed = []
        text_indices = []
        
        # Check cache
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                embeddings.append(self._cache[cache_key])
            else:
                texts_to_embed.append(text)
                text_indices.append(i)
                embeddings.append(None)
        
        # Generate embeddings for uncached texts
        if texts_to_embed:
            new_embeddings = await self._generate_embeddings(texts_to_embed)
            
            for text, embedding in zip(texts_to_embed, new_embeddings):
                cache_key = self._get_cache_key(text)
                self._cache[cache_key] = embedding
                idx = text_indices.pop(0)
                embeddings[idx] = embedding
        
        return embeddings
    
    async def embed_chunks(self, chunks: List[Any]) -> List[Any]:
        """Generate embeddings for chunk objects."""
        chunks_to_embed = [c for c in chunks if c.embedding is None]
        chunks_with_embedding = [c for c in chunks if c.embedding is not None]
        
        if chunks_to_embed:
            texts = [chunk.text for chunk in chunks_to_embed]
            embeddings = await self.embed_texts(texts)
            
            for chunk, embedding in zip(chunks_to_embed, embeddings):
                chunk.embedding = embedding
        
        return chunks_with_embedding + chunks_to_embed
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using available provider."""
        
        # Try Ollama first (local, free)
        try:
            return await self._ollama_embeddings(texts)
        except Exception as e:
            logger.warning(f"Ollama embedding failed: {e}")
        
        # Try Groq (if API key set)
        if settings.groq.API_KEY:
            try:
                return await self._groq_embeddings(texts)
            except Exception as e:
                logger.warning(f"Groq embedding failed: {e}")
        
        # Try OpenAI (if API key set)
        if settings.llm.OPENAI_API_KEY:
            try:
                return await self._openai_embeddings(texts)
            except Exception as e:
                logger.warning(f"OpenAI embedding failed: {e}")
        
        # Fallback: Sentence-Transformers (local)
        return await self._sentence_transformer_embeddings(texts)
    
    async def _ollama_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama (local)."""
        import aiohttp
        
        model = settings.ollama.EMBEDDING_MODEL
        base_url = settings.ollama.BASE_URL.rstrip('/')
        embeddings = []
        
        logger.info(f"Using Ollama embeddings: {model}")
        
        async with aiohttp.ClientSession() as session:
            for text in texts:
                async with session.post(
                    f"{base_url}/api/embeddings",
                    json={"model": model, "prompt": text},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"Ollama error ({response.status}): {error_text[:200]}")
                    result = await response.json()
                    emb = result.get("embedding", [])
                    if emb:
                        embeddings.append(emb)
                    else:
                        raise ValueError("Ollama returned empty embedding")
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings via Ollama")
        return embeddings
    
    async def _groq_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Groq."""
        # Groq doesn't have a dedicated embedding endpoint yet
        # Use a simple hash-based fallback for now
        logger.warning("Groq doesn't support embeddings yet. Using hash-based fallback.")
        
        embeddings = []
        for text in texts:
            # Simple deterministic embedding from text hash
            hash_bytes = hashlib.sha256(text.encode()).digest()
            embedding = [float(b) / 255.0 for b in hash_bytes[:32]]
            # Pad or truncate to dimension
            if len(embedding) < self.dimension:
                embedding.extend([0.0] * (self.dimension - len(embedding)))
            else:
                embedding = embedding[:self.dimension]
            embeddings.append(embedding)
        
        return embeddings
    
    async def _openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI."""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=settings.llm.OPENAI_API_KEY)
        response = await client.embeddings.create(
            model=self.model_name,
            input=texts,
        )
        
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in embeddings]
    
    async def _sentence_transformer_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Sentence-Transformers (local fallback)."""
        from sentence_transformers import SentenceTransformer
        
        model_name = self.model_name
        if model_name.startswith("sentence-transformers/"):
            model_name = model_name.replace("sentence-transformers/", "")
        
        logger.info(f"Using Sentence-Transformers: {model_name}")
        
        if not self._st_model:
            self._st_model = SentenceTransformer(model_name)
        
        embeddings = await asyncio.to_thread(
            self._st_model.encode,
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        
        return embeddings.tolist()
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return f"{self.model_name}:{hashlib.sha256(text.encode()).hexdigest()}"
    
    def normalize_embedding(self, embedding: List[float]) -> List[float]:
        """L2 normalize embedding."""
        arr = np.array(embedding)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr.tolist()
    
    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        arr1 = np.array(emb1)
        arr2 = np.array(emb2)
        
        dot = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot / (norm1 * norm2))
    
    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self._cache = {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "model": self.model_name,
            "dimension": self.dimension,
            "cache_size": len(self._cache),
        }
