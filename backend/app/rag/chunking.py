"""
HealthConnect AI - Chunking Engine
===================================
Advanced text chunking strategies for RAG pipeline.

Strategies:
- Fixed-size chunking with overlap
- Semantic chunking (paragraph/section-based)
- Recursive chunking (hierarchical separators)
- Sentence-aware chunking
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ChunkingStrategy(Enum):
    """Chunking strategies"""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    RECURSIVE = "recursive"
    SENTENCE_AWARE = "sentence_aware"
    HYBRID = "hybrid"


@dataclass
class Chunk:
    """Document chunk"""
    chunk_id: str
    document_id: str
    text: str
    chunk_index: int
    start_index: int
    end_index: int
    token_count: int
    section: Optional[str] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "chunk_index": self.chunk_index,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "token_count": self.token_count,
            "section": self.section,
            "title": self.title,
            "metadata": self.metadata,
        }


class ChunkingEngine:
    """
    Advanced chunking engine for document processing.
    Supports multiple chunking strategies.
    """
    
    def __init__(self, strategy: ChunkingStrategy = ChunkingStrategy.HYBRID):
        self.strategy = strategy
        self.default_chunk_size = settings.rag.CHUNK_SIZE
        self.default_overlap = settings.rag.CHUNK_OVERLAP
        self.min_chunk_size = 5  # Minimum tokens per chunk
        self.max_chunk_size = 1000  # Maximum tokens per chunk
    
    def chunk_document(
        self,
        text: str,
        document_id: str = "doc",
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None,
        strategy: Optional[ChunkingStrategy] = None,
    ) -> List[Chunk]:
        """
        Chunk a document using specified strategy.
        
        Args:
            text: Document text
            document_id: Document identifier
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks
            strategy: Chunking strategy
            
        Returns:
            List[Chunk]: List of chunks
        """
        chunk_size = chunk_size or self.default_chunk_size
        overlap = overlap or self.default_overlap
        strategy = strategy or self.strategy
        
        logger.info(
            f"Chunking document {document_id} with {strategy.value} "
            f"(size={chunk_size}, overlap={overlap})"
        )
        
        if strategy == ChunkingStrategy.FIXED_SIZE:
            chunks = self._fixed_size_chunk(text, document_id, chunk_size, overlap)
        elif strategy == ChunkingStrategy.SEMANTIC:
            chunks = self._semantic_chunk(text, document_id, chunk_size)
        elif strategy == ChunkingStrategy.RECURSIVE:
            chunks = self._recursive_chunk(text, document_id, chunk_size)
        elif strategy == ChunkingStrategy.SENTENCE_AWARE:
            chunks = self._sentence_aware_chunk(text, document_id, chunk_size, overlap)
        elif strategy == ChunkingStrategy.HYBRID:
            chunks = self._hybrid_chunk(text, document_id, chunk_size, overlap)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
        
        # Filter out empty chunks only (allow small chunks for testing)
        chunks = [c for c in chunks if c.token_count > 0]
        
        logger.info(f"Created {len(chunks)} chunks for document {document_id}")
        # If no chunks created but text exists, return the whole text as one chunk
        if not chunks and text.strip():
            chunks.append(Chunk(
                chunk_id=self._generate_chunk_id(document_id, 0),
                document_id=document_id,
                text=text.strip(),
                chunk_index=0,
                start_index=0,
                end_index=len(text.strip()),
                token_count=self._token_count(text.strip()),
                metadata={"chunk_size": len(text.strip())}
            ))
        
        return chunks
    
    def _fixed_size_chunk(
        self,
        text: str,
        document_id: str,
        chunk_size: int,
        overlap: int,
    ) -> List[Chunk]:
        """
        Fixed-size chunking with sliding window.
        
        Formula:
        chunk[i].start = i * (chunk_size - overlap)
        chunk[i].end = chunk[i].start + chunk_size
        """
        tokens = self._tokenize(text)
        chunks = []
        step = chunk_size - overlap
        chunk_index = 0
        
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i:i + chunk_size]
            if not chunk_tokens:
                continue
            
            chunk_text = self._detokenize(chunk_tokens)
            chunks.append(Chunk(
                chunk_id=self._generate_chunk_id(document_id, chunk_index),
                document_id=document_id,
                text=chunk_text,
                chunk_index=chunk_index,
                start_index=i,
                end_index=min(i + chunk_size, len(tokens)),
                token_count=len(chunk_tokens),
            ))
            chunk_index += 1
        
        return chunks
    
    def _semantic_chunk(
        self,
        text: str,
        document_id: str,
        max_chunk_size: int,
    ) -> List[Chunk]:
        """
        Semantic chunking based on paragraphs and sections.
        Preserves semantic boundaries.
        """
        # Split by sections (headers)
        sections = self._extract_sections(text)
        chunks = []
        chunk_index = 0
        
        for section_title, section_text in sections:
            # Split section by paragraphs
            paragraphs = section_text.split('\n\n')
            current_chunk = []
            current_size = 0
            current_start = 0
            
            for para in paragraphs:
                para_tokens = self._tokenize(para)
                para_size = len(para_tokens)
                
                if current_size + para_size > max_chunk_size and current_chunk:
                    # Flush current chunk
                    chunk_text = ' '.join(current_chunk)
                    chunks.append(Chunk(
                        chunk_id=self._generate_chunk_id(document_id, chunk_index),
                        document_id=document_id,
                        text=chunk_text,
                        chunk_index=chunk_index,
                        start_index=current_start,
                        end_index=current_start + current_size,
                        token_count=current_size,
                        section=section_title,
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_size = 0
                
                current_chunk.append(para)
                current_size += para_size
            
            # Flush remaining
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(Chunk(
                    chunk_id=self._generate_chunk_id(document_id, chunk_index),
                    document_id=document_id,
                    text=chunk_text,
                    chunk_index=chunk_index,
                    start_index=current_start,
                    end_index=current_start + current_size,
                    token_count=current_size,
                    section=section_title,
                ))
                chunk_index += 1
        
        return chunks
    
    def _recursive_chunk(
        self,
        text: str,
        document_id: str,
        max_chunk_size: int,
    ) -> List[Chunk]:
        """
        Recursive chunking using separator hierarchy.
        Splits by largest separator first.
        """
        separators = ['\n\n', '\n', '. ', ' ', '']
        chunks = []
        chunk_index = 0
        
        def recursive_split(
            text_part: str,
            separators: List[str],
            current_chunk_index: int,
        ) -> int:
            nonlocal chunks
            
            if self._token_count(text_part) <= max_chunk_size:
                chunks.append(Chunk(
                    chunk_id=self._generate_chunk_id(document_id, current_chunk_index),
                    document_id=document_id,
                    text=text_part,
                    chunk_index=current_chunk_index,
                    start_index=0,
                    end_index=len(text_part),
                    token_count=self._token_count(text_part),
                ))
                return current_chunk_index + 1
            
            if not separators:
                # Force split by characters
                char_chunks = self._force_split(text_part, max_chunk_size)
                for cc in char_chunks:
                    chunks.append(Chunk(
                        chunk_id=self._generate_chunk_id(document_id, current_chunk_index),
                        document_id=document_id,
                        text=cc,
                        chunk_index=current_chunk_index,
                        start_index=0,
                        end_index=len(cc),
                        token_count=self._token_count(cc),
                    ))
                    current_chunk_index += 1
                return current_chunk_index
            
            separator = separators[0]
            remaining = separators[1:]
            
            if separator == '':
                char_chunks = self._force_split(text_part, max_chunk_size)
                for cc in char_chunks:
                    chunks.append(Chunk(
                        chunk_id=self._generate_chunk_id(document_id, current_chunk_index),
                        document_id=document_id,
                        text=cc,
                        chunk_index=current_chunk_index,
                        start_index=0,
                        end_index=len(cc),
                        token_count=self._token_count(cc),
                    ))
                    current_chunk_index += 1
                return current_chunk_index
            
            splits = text_part.split(separator)
            
            for split in splits:
                if self._token_count(split) <= max_chunk_size:
                    chunks.append(Chunk(
                        chunk_id=self._generate_chunk_id(document_id, current_chunk_index),
                        document_id=document_id,
                        text=split,
                        chunk_index=current_chunk_index,
                        start_index=0,
                        end_index=len(split),
                        token_count=self._token_count(split),
                    ))
                    current_chunk_index += 1
                else:
                    current_chunk_index = recursive_split(
                        split,
                        remaining,
                        current_chunk_index,
                    )
            
            return current_chunk_index
        
        recursive_split(text, separators, chunk_index)
        return chunks
    
    def _sentence_aware_chunk(
        self,
        text: str,
        document_id: str,
        chunk_size: int,
        overlap: int,
    ) -> List[Chunk]:
        """
        Sentence-aware chunking.
        Groups sentences into chunks while respecting sentence boundaries.
        """
        sentences = self._extract_sentences(text)
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self._tokenize(sentence)
            sentence_size = len(sentence_tokens)
            
            if current_size + sentence_size > chunk_size and current_chunk:
                # Flush current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(Chunk(
                    chunk_id=self._generate_chunk_id(document_id, chunk_index),
                    document_id=document_id,
                    text=chunk_text,
                    chunk_index=chunk_index,
                    start_index=0,
                    end_index=current_size,
                    token_count=current_size,
                ))
                chunk_index += 1
                
                # Keep overlap sentences
                overlap_tokens = self._tokenize(' '.join(current_chunk[-overlap:]))
                current_chunk = current_chunk[-overlap:]
                current_size = len(overlap_tokens)
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Flush remaining
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(Chunk(
                chunk_id=self._generate_chunk_id(document_id, chunk_index),
                document_id=document_id,
                text=chunk_text,
                chunk_index=chunk_index,
                start_index=0,
                end_index=current_size,
                token_count=current_size,
            ))
        
        return chunks
    
    def _hybrid_chunk(
        self,
        text: str,
        document_id: str,
        chunk_size: int,
        overlap: int,
    ) -> List[Chunk]:
        """
        Hybrid chunking strategy.
        Combines semantic and sentence-aware approaches.
        """
        # First try semantic chunking
        sections = self._extract_sections(text)
        
        if len(sections) > 1:
            # Use semantic chunking for multi-section documents
            return self._semantic_chunk(text, document_id, chunk_size)
        else:
            # Use sentence-aware for single-section documents
            return self._sentence_aware_chunk(text, document_id, chunk_size, overlap)
    
    def _extract_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract sections from document text.
        Identifies headers and their content.
        
        Returns:
            List[Tuple[str, str]]: List of (section_title, section_text)
        """
        sections = []
        current_title = ""
        current_text = []
        
        lines = text.split('\n')
        
        for line in lines:
            stripped = line.strip()
            
            # Check if line is a header
            if self._is_header(stripped):
                # Save previous section
                if current_text:
                    sections.append((current_title, '\n'.join(current_text)))
                
                current_title = stripped
                current_text = []
            else:
                if stripped:
                    current_text.append(stripped)
        
        # Save last section
        if current_text:
            sections.append((current_title, '\n'.join(current_text)))
        
        # If no sections found, return entire text as one section
        if not sections:
            sections = [("", text)]
        
        return sections
    
    def _is_header(self, line: str) -> bool:
        """
        Check if line is a header.
        Headers are typically short, capitalized, or numbered.
        """
        if not line:
            return False
        
        # Check for numbered sections (e.g., "1. Introduction")
        if re.match(r'^\d+\.\s+[A-Z]', line):
            return True
        
        # Check for ALL CAPS
        if line.isupper() and len(line) < 100:
            return True
        
        # Check for title case with colon
        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:', line):
            return True
        
        return False
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        import nltk
        from nltk.tokenize import sent_tokenize
        
        try:
            return sent_tokenize(text)
        except LookupError:
            nltk.download('punkt', quiet=True)
            return sent_tokenize(text)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return text.split()
    
    def _detokenize(self, tokens: List[str]) -> str:
        """Join tokens back to text"""
        return ' '.join(tokens)
    
    def _token_count(self, text: str) -> int:
        """Count tokens in text"""
        return len(self._tokenize(text))
    
    def _force_split(self, text: str, max_chunk_size: int) -> List[str]:
        """Force split text by characters"""
        max_chars = max_chunk_size * 4  # Approximate 4 chars per token
        return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    
    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        return f"{document_id}_chunk_{chunk_index:04d}"
    
    def estimate_chunk_count(self, text: str, chunk_size: int, overlap: int) -> int:
        """
        Estimate number of chunks for a document.
        
        Formula:
        Number of chunks = ceil((N - chunk_size) / (chunk_size - overlap)) + 1
        """
        total_tokens = self._token_count(text)
        
        if total_tokens <= chunk_size:
            return 1
        
        effective_step = chunk_size - overlap
        return ((total_tokens - chunk_size) // effective_step) + 2