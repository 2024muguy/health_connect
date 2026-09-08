"""
HealthConnect AI - Citation Generator
======================================
Generates citations for RAG responses.

Features:
- Source citation formatting
- In-text citations
- Reference list generation
- Citation validation
"""

from typing import List, Dict, Any, Optional
import re

from config.logging_config import get_logger

logger = get_logger(__name__)


class CitationGenerator:
    """
    Citation generator for RAG responses.
    Formats and validates source citations.
    """
    
    def __init__(self):
        self.citation_style = "bracketed"  # [1], [2], etc.
    
    def generate_citations(
        self,
        sources: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """
        Generate formatted citations for sources.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            List[Dict[str, str]]: Formatted citations
        """
        citations = []
        
        for source in sources:
            citation = {
                "index": str(source.get("index", "")),
                "chunk_id": source.get("chunk_id", ""),
                "document_id": source.get("document_id", ""),
                "section": source.get("section", ""),
                "title": source.get("title", ""),
                "formatted": self._format_citation(source),
            }
            citations.append(citation)
        
        return citations
    
    def _format_citation(self, source: Dict[str, Any]) -> str:
        """Format a single citation"""
        parts = []
        
        index = source.get("index", "")
        if index:
            parts.append(f"[{index}]")
        
        title = source.get("title", "")
        if title:
            parts.append(title)
        
        section = source.get("section", "")
        if section:
            parts.append(f"Section: {section}")
        
        chunk_id = source.get("chunk_id", "")
        if chunk_id:
            parts.append(f"Source: {chunk_id}")
        
        return " - ".join(parts) if parts else "Unknown source"
    
    def add_in_text_citations(
        self,
        text: str,
        sources: List[Dict[str, Any]],
    ) -> str:
        """
        Add in-text citations to response text.
        
        Args:
            text: Response text
            sources: Source list
            
        Returns:
            str: Text with citations
        """
        if not sources:
            return text
        
        # Create citation markers
        markers = [f"[{s.get('index', i + 1)}]" for i, s in enumerate(sources, 1)]
        
        # Simple approach: append citations at end of relevant sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cited_sentences = []
        
        for i, sentence in enumerate(sentences):
            cited_sentences.append(sentence)
            
            # Add citation to every few sentences
            if (i + 1) % 2 == 0 and markers:
                citation = markers.pop(0)
                cited_sentences[-1] += f" {citation}"
        
        return ' '.join(cited_sentences)
    
    def generate_reference_list(
        self,
        sources: List[Dict[str, Any]],
    ) -> str:
        """
        Generate a reference list from sources.
        
        Args:
            sources: List of sources
            
        Returns:
            str: Formatted reference list
        """
        if not sources:
            return ""
        
        references = ["\nReferences:"]
        
        for source in sources:
            citation = self._format_citation(source)
            references.append(f"  {citation}")
        
        return "\n".join(references)
    
    def validate_citations(
        self,
        response_text: str,
        sources: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validate that citations in response match provided sources.
        
        Args:
            response_text: Response with citations
            sources: Provided sources
            
        Returns:
            Dict: Validation result
        """
        # Extract citation markers from response
        citation_pattern = r'\[(\d+)\]'
        cited_indices = [int(m) for m in re.findall(citation_pattern, response_text)]
        
        valid_indices = [s.get("index", i + 1) for i, s in enumerate(sources, 1)]
        valid_indices = [int(i) for i in valid_indices]
        
        invalid_citations = [i for i in cited_indices if i not in valid_indices]
        missing_citations = [i for i in valid_indices if i not in cited_indices]
        
        return {
            "valid": len(invalid_citations) == 0,
            "cited_count": len(cited_indices),
            "source_count": len(sources),
            "invalid_citations": invalid_citations,
            "missing_citations": missing_citations,
        }
    
    def extract_claims(
        self,
        response_text: str,
    ) -> List[str]:
        """
        Extract factual claims from response text.
        
        Args:
            response_text: Response text
            
        Returns:
            List[str]: Extracted claims
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', response_text)
        
        # Filter out questions and non-factual statements
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or sentence.endswith('?'):
                continue
            
            # Skip conversational phrases
            if any(phrase in sentence.lower() for phrase in [
                "i apologize", "thank you", "is there anything",
                "would you like", "i can help",
            ]):
                continue
            
            claims.append(sentence)
        
        return claims
    
    def check_claim_support(
        self,
        claim: str,
        context: str,
    ) -> bool:
        """
        Check if a claim is supported by context.
        Simple keyword overlap check.
        
        Args:
            claim: Claim to check
            context: Context text
            
        Returns:
            bool: True if claim is likely supported
        """
        # Extract key terms from claim
        claim_terms = set(re.findall(r'\w+', claim.lower()))
        context_terms = set(re.findall(r'\w+', context.lower()))
        
        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                     'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are',
                     'was', 'were', 'be', 'been', 'being'}
        
        claim_terms = claim_terms - stopwords
        context_terms = context_terms - stopwords
        
        if not claim_terms:
            return True
        
        # Calculate overlap
        overlap = claim_terms.intersection(context_terms)
        overlap_ratio = len(overlap) / len(claim_terms)
        
        return overlap_ratio >= 0.5