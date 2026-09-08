"""
HealthConnect AI - Vector Store Manager
========================================
Vector database management for RAG pipeline.

Features:
- Pinecone integration
- FAISS fallback
- ChromaDB support
- Batch operations
- Metadata management
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.rag.chunking import Chunk

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class VectorStoreManager:
    """
    Vector store manager for RAG pipeline.
    Manages vector database operations.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.index_type = self._determine_index_type()
        self.index = None
        self._chunk_map: Dict[str, Chunk] = {}
        logger.info(f"VectorStoreManager initialized with {self.index_type}")
    
    def _determine_index_type(self) -> str:
        """Determine which vector store to use"""
        if settings.vector_db.API_KEY and settings.vector_db.ENVIRONMENT:
            return "pinecone"
        
        # Try FAISS
        try:
            import faiss
            return "faiss"
        except ImportError:
            pass
        
        # Try ChromaDB
        try:
            import chromadb
            return "chroma"
        except ImportError:
            pass
        
        # Fallback to in-memory
        return "memory"
    
    async def initialize(self) -> None:
        """Initialize vector store"""
        if self.index_type == "pinecone":
            await self._init_pinecone()
        elif self.index_type == "faiss":
            await self._init_faiss()
        elif self.index_type == "chroma":
            await self._init_chroma()
        else:
            await self._init_memory()
    
    async def _init_pinecone(self) -> None:
        """Initialize Pinecone"""
        import pinecone
        
        pinecone.init(
            api_key=settings.vector_db.API_KEY,
            environment=settings.vector_db.ENVIRONMENT,
        )
        
        index_name = settings.vector_db.INDEX_NAME
        
        # Create index if not exists
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=settings.vector_db.DIMENSION,
                metric=settings.vector_db.METRIC,
            )
            logger.info(f"Created Pinecone index: {index_name}")
        
        self.index = pinecone.Index(index_name)
        logger.info(f"Connected to Pinecone index: {index_name}")
    
    async def _init_faiss(self) -> None:
        """Initialize FAISS"""
        import faiss
        
        dimension = settings.vector_db.DIMENSION
        self.index = faiss.IndexHNSWFlat(dimension, 32)
        self.index.hnsw.efConstruction = 200
        logger.info(f"Initialized FAISS index (dimension={dimension})")
    
    async def _init_chroma(self) -> None:
        """Initialize ChromaDB"""
        import chromadb
        
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name=settings.vector_db.INDEX_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"Initialized ChromaDB collection: {settings.vector_db.INDEX_NAME}")
    
    async def _init_memory(self) -> None:
        """Initialize in-memory store"""
        self._embeddings = []
        self._chunks = []
        logger.info("Initialized in-memory vector store")
    
    async def upsert_chunks(self, chunks: List[Chunk]) -> int:
        """
        Insert or update chunks in vector store.
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            int: Number of chunks indexed
        """
        if not chunks:
            return 0
        
        if self.index_type == "pinecone":
            return await self._upsert_pinecone(chunks)
        elif self.index_type == "faiss":
            return await self._upsert_faiss(chunks)
        elif self.index_type == "chroma":
            return await self._upsert_chroma(chunks)
        else:
            return await self._upsert_memory(chunks)
    
    async def _upsert_pinecone(self, chunks: List[Chunk]) -> int:
        """Upsert chunks to Pinecone"""
        vectors = []
        
        for chunk in chunks:
            if chunk.embedding is None:
                continue
            
            vectors.append((
                chunk.chunk_id,
                chunk.embedding,
                {
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                    "section": chunk.section or "",
                    "title": chunk.title or "",
                    **chunk.metadata,
                }
            ))
            
            self._chunk_map[chunk.chunk_id] = chunk
        
        # Batch upsert (100 at a time)
        batch_size = 100
        total_indexed = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            total_indexed += len(batch)
        
        return total_indexed
    
    async def _upsert_faiss(self, chunks: List[Chunk]) -> int:
        """Upsert chunks to FAISS"""
        embeddings = []
        
        for chunk in chunks:
            if chunk.embedding is None:
                continue
            
            embeddings.append(chunk.embedding)
            self._chunk_map[chunk.chunk_id] = chunk
        
        if embeddings:
            embeddings_array = np.array(embeddings, dtype='float32')
            self.index.add(embeddings_array)
        
        return len(embeddings)
    
    async def _upsert_chroma(self, chunks: List[Chunk]) -> int:
        """Upsert chunks to ChromaDB"""
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            if chunk.embedding is None:
                continue
            
            ids.append(chunk.chunk_id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.text)
            metadatas.append({
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                **chunk.metadata,
            })
            self._chunk_map[chunk.chunk_id] = chunk
        
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        
        return len(ids)
    
    async def _upsert_memory(self, chunks: List[Chunk]) -> int:
        """Upsert chunks to memory"""
        for chunk in chunks:
            if chunk.embedding is None:
                continue
            
            self._embeddings.append(chunk.embedding)
            self._chunks.append(chunk)
            self._chunk_map[chunk.chunk_id] = chunk
        
        return len(self._chunks)
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results
            filters: Metadata filters
            
        Returns:
            List[Tuple[str, float, Dict]]: (chunk_id, score, metadata)
        """
        if self.index_type == "pinecone":
            return await self._search_pinecone(query_embedding, top_k, filters)
        elif self.index_type == "faiss":
            return await self._search_faiss(query_embedding, top_k)
        elif self.index_type == "chroma":
            return await self._search_chroma(query_embedding, top_k)
        else:
            return await self._search_memory(query_embedding, top_k)
    
    async def _search_pinecone(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict],
    ) -> List[Tuple[str, float, Dict]]:
        """Search Pinecone"""
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filters,
            include_metadata=True,
        )
        
        return [
            (match["id"], match["score"], match.get("metadata", {}))
            for match in results["matches"]
        ]
    
    async def _search_faiss(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[Tuple[str, float, Dict]]:
        """Search FAISS"""
        query_array = np.array([query_embedding], dtype='float32')
        distances, indices = self.index.search(query_array, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self._chunks):
                chunk = self._chunks[idx]
                similarity = 1 - distances[0][i]
                results.append((
                    chunk.chunk_id,
                    similarity,
                    {
                        "document_id": chunk.document_id,
                        "text": chunk.text,
                        "section": chunk.section,
                    }
                ))
        
        return results
    
    async def _search_chroma(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[Tuple[str, float, Dict]]:
        """Search ChromaDB"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        
        output = []
        for i, chunk_id in enumerate(results["ids"][0]):
            score = 1 - results["distances"][0][i]
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            output.append((chunk_id, score, metadata))
        
        return output
    
    async def _search_memory(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[Tuple[str, float, Dict]]:
        """Search in-memory store"""
        if not self._embeddings:
            return []
        
        embeddings_array = np.array(self._embeddings)
        query_array = np.array(query_embedding)
        
        # Cosine similarity
        similarities = np.dot(embeddings_array, query_array) / (
            np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_array)
        )
        
        # Get top-k
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            chunk = self._chunks[idx]
            results.append((
                chunk.chunk_id,
                float(similarities[idx]),
                {
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "section": chunk.section,
                }
            ))
        
        return results
    
    async def delete_chunks(self, chunk_ids: List[str]) -> int:
        """Delete chunks from vector store"""
        if self.index_type == "pinecone":
            self.index.delete(ids=chunk_ids)
        elif self.index_type == "faiss":
            logger.warning("FAISS does not support deletion")
        elif self.index_type == "chroma":
            self.collection.delete(ids=chunk_ids)
        
        # Remove from chunk map
        for chunk_id in chunk_ids:
            self._chunk_map.pop(chunk_id, None)
        
        return len(chunk_ids)
    
    async def clear(self) -> None:
        """Clear all data from vector store"""
        if self.index_type == "pinecone":
            self.index.delete(delete_all=True)
        elif self.index_type == "faiss":
            self.index.reset()
        elif self.index_type == "chroma":
            self.client.delete_collection(settings.vector_db.INDEX_NAME)
            self.collection = self.client.create_collection(
                name=settings.vector_db.INDEX_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        
        self._chunk_map = {}
        logger.info("Vector store cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if self.index_type == "pinecone":
            stats = self.index.describe_index_stats()
            return {
                "type": "pinecone",
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", settings.vector_db.DIMENSION),
                "namespaces": stats.get("namespaces", {}),
            }
        
        return {
            "type": self.index_type,
            "total_vectors": len(self._chunk_map),
        }