"""
HealthConnect AI - Text Processing Utilities
=============================================
Text cleaning, normalization, and processing functions.

Features:
- Unicode normalization
- Whitespace cleaning
- Tokenization
- Text chunking
- Keyword extraction
"""

import re
import unicodedata
from typing import List, Optional, Set, Dict, Tuple
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# English stopwords
STOPWORDS: Set[str] = set(stopwords.words('english'))

# Medical stopwords to add
MEDICAL_STOPWORDS: Set[str] = {
    'patient', 'doctor', 'clinic', 'appointment', 'healthcare',
    'medical', 'hospital', 'treatment', 'service',
}

# Combined stopwords
ALL_STOPWORDS = STOPWORDS.union(MEDICAL_STOPWORDS)


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Operations:
    1. Unicode normalization (NFKC)
    2. Remove control characters
    3. Normalize quotes and dashes
    4. Remove extra whitespace
    5. Strip leading/trailing whitespace
    
    Args:
        text: Input text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    # Normalize quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    
    # Normalize dashes
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u2015', '-')
    
    # Remove extra whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison and matching.
    
    Operations:
    1. Convert to lowercase
    2. Remove punctuation
    3. Remove extra whitespace
    
    Args:
        text: Input text
        
    Returns:
        str: Normalized text
    """
    text = clean_text(text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize_text(text: str, remove_stopwords: bool = False) -> List[str]:
    """
    Tokenize text into words.
    
    Args:
        text: Input text
        remove_stopwords: Whether to remove stopwords
        
    Returns:
        List[str]: List of tokens
    """
    text = clean_text(text)
    tokens = word_tokenize(text.lower())
    
    if remove_stopwords:
        tokens = [t for t in tokens if t not in ALL_STOPWORDS]
    
    return tokens


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 77,
    by_sentences: bool = False,
) -> List[Dict[str, any]]:
    """
    Chunk text into overlapping segments.
    
    Args:
        text: Input text
        chunk_size: Target chunk size in tokens
        overlap: Number of overlapping tokens
        by_sentences: Whether to chunk by sentences
        
    Returns:
        List[Dict]: List of chunks with metadata
    """
    text = clean_text(text)
    
    if by_sentences:
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_tokens = len(word_tokenize(sentence))
            
            if current_size + sentence_tokens > chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'id': f'chunk_{chunk_id}',
                    'text': chunk_text,
                    'token_count': current_size,
                })
                chunk_id += 1
                current_chunk = []
                current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_tokens
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'id': f'chunk_{chunk_id}',
                'text': chunk_text,
                'token_count': current_size,
            })
        
        return chunks
    else:
        tokens = word_tokenize(text)
        chunks = []
        step = chunk_size - overlap
        
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i:i + chunk_size]
            if len(chunk_tokens) < 10:  # Skip very small chunks
                continue
            
            chunk_text = ' '.join(chunk_tokens)
            chunks.append({
                'id': f'chunk_{len(chunks)}',
                'text': chunk_text,
                'token_count': len(chunk_tokens),
                'start_index': i,
                'end_index': min(i + chunk_size, len(tokens)),
            })
        
        return chunks


def extract_keywords(
    text: str,
    max_keywords: int = 10,
    min_length: int = 3,
) -> List[str]:
    """
    Extract keywords from text using frequency analysis.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords
        min_length: Minimum keyword length
        
    Returns:
        List[str]: Extracted keywords
    """
    from collections import Counter
    
    tokens = tokenize_text(text, remove_stopwords=True)
    tokens = [t for t in tokens if len(t) >= min_length]
    
    # Count frequencies
    freq = Counter(tokens)
    
    # Return top keywords
    return [word for word, _ in freq.most_common(max_keywords)]


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate text similarity using Jaccard similarity.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        float: Similarity score (0-1)
    """
    tokens1 = set(tokenize_text(text1))
    tokens2 = set(tokenize_text(text2))
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    
    return len(intersection) / len(union)


def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "...",
) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to append when truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix