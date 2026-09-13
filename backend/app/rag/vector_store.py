"""
HealthConnect AI - Vector Store Manager (Production Ready)
==========================================================
Vector database management for RAG pipeline.
Auto-loads from persisted FAISS index or builds from JSON data.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.rag.chunking import Chunk

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class VectorStoreManager:
    """Vector store manager with automatic persistence."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.index_type = "faiss"  # Always use FAISS locally
        self.index = None
        self._chunk_map: Dict[str, Chunk] = {}
        self._embeddings: List[np.ndarray] = []
        self._chunks: List[Chunk] = []
        
        # Persistence paths
        self.index_file = Path("data/processed/faiss_index.bin")
        self.data_file = Path("data/processed/rag_knowledge_base.json")
        
        # Auto-initialize
        self._auto_load()
        
        logger.info(f"VectorStoreManager initialized with {self.index_type}")
    
    def _auto_load(self):
        """Auto-load index from disk or build from JSON data."""
        import faiss
        
        # Try loading FAISS index
        if self.index_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                logger.info(f"✅ Loaded FAISS index: {self.index.ntotal} vectors")
                
                # Load chunk data
                if self.data_file.exists():
                    with open(self.data_file) as f:
                        data = json.load(f)
                    
                    for item in data:
                        chunk = Chunk(
                            chunk_id=item.get("id", ""),
                            document_id=item.get("metadata", {}).get("document", "unknown"),
                            text=item.get("text", ""),
                            chunk_index=item.get("metadata", {}).get("chunk", 0),
                            start_index=0,
                            end_index=len(item.get("text", "")),
                            token_count=len(item.get("text", "").split()),
                            embedding=item.get("embedding"),
                        )
                        self._chunks.append(chunk)
                        self._chunk_map[chunk.chunk_id] = chunk
                    
                    logger.info(f"✅ Loaded {len(self._chunks)} chunks from JSON")
                return
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")
        
        # Build from JSON data
        if self.data_file.exists():
            try:
                with open(self.data_file) as f:
                    data = json.load(f)
                
                if data:
                    embeddings = np.array(
                        [item["embedding"] for item in data if item.get("embedding")],
                        dtype=np.float32
                    )
                    
                    if len(embeddings) > 0:
                        dimension = embeddings.shape[1]
                        self.index = faiss.IndexFlatL2(dimension)
                        self.index.add(embeddings)
                        
                        for item in data:
                            chunk = Chunk(
                                chunk_id=item.get("id", ""),
                                document_id=item.get("metadata", {}).get("document", "unknown"),
                                text=item.get("text", ""),
                                chunk_index=item.get("metadata", {}).get("chunk", 0),
                                start_index=0,
                                end_index=len(item.get("text", "")),
                                token_count=len(item.get("text", "").split()),
                                embedding=item.get("embedding"),
                            )
                            self._chunks.append(chunk)
                            self._chunk_map[chunk.chunk_id] = chunk
                        
                        # Save index for future use
                        faiss.write_index(self.index, str(self.index_file))
                        logger.info(f"✅ Built FAISS index from JSON: {self.index.ntotal} vectors")
                        return
            except Exception as e:
                logger.warning(f"Failed to build from JSON: {e}")
        
        # Create empty index
        try:
            self.index = faiss.IndexFlatL2(768)  # Ollama nomic-embed-text dimension
            logger.info("Created empty FAISS index (768 dims)")
        except Exception as e:
            logger.error(f"FAISS initialization failed: {e}")
            self.index = None
    
    async def initialize(self) -> None:
        """Initialize vector store (called by events)."""
        # Already initialized in __init__
        logger.info(f"Vector store ready: {self.index_type} ({self.index.ntotal if self.index else 0} vectors)")
    
    async def upsert_chunks(self, chunks: List[Chunk]) -> int:
        """Insert or update chunks in vector store."""
        import faiss
        
        embeddings = []
        
        for chunk in chunks:
            if chunk.embedding is None:
                continue
            embeddings.append(chunk.embedding)
            self._chunk_map[chunk.chunk_id] = chunk
            self._chunks.append(chunk)
        
        if embeddings:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            if self.index is None or self.index.ntotal == 0:
                dimension = embeddings_array.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
            
            self.index.add(embeddings_array)
            
            # Persist
            faiss.write_index(self.index, str(self.index_file))
            logger.info(f"✅ Indexed {len(embeddings)} chunks (total: {self.index.ntotal})")
        
        return len(embeddings)
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar chunks."""
        if self.index is None or self.index.ntotal == 0:
            logger.debug("FAISS index is empty")
            return []
        
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self._chunks):
                chunk = self._chunks[idx]
                similarity = 1.0 / (1.0 + distances[0][i])
                results.append((
                    chunk.chunk_id,
                    float(similarity),
                    {"document_id": chunk.document_id, "text": chunk.text, "section": chunk.section},
                ))
        
        return results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "type": self.index_type,
            "total_vectors": self.index.ntotal if self.index else 0,
            "chunks_loaded": len(self._chunks),
            "index_file": str(self.index_file),
        }
