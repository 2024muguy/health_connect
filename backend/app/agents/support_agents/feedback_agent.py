"""
HealthConnect AI - Feedback Agent
==================================
Collects and processes user feedback.

Features:
- Feedback collection
- Sentiment analysis
- Satisfaction tracking
- Feedback categorization
"""

import time
from typing import List, Dict, Any, Optional
import re

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)

from config.logging_config import get_logger

logger = get_logger(__name__)


class FeedbackAgent(BaseAgent):
    """
    Feedback Agent.
    Collects and analyzes user feedback.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.FEEDBACK, config)
        
        # Sentiment indicators
        self.positive_terms = [
            'thank', 'great', 'good', 'excellent', 'awesome', 'helpful',
            'wonderful', 'perfect', 'amazing', 'fantastic', 'appreciate',
        ]
        
        self.negative_terms = [
            'bad', 'terrible', 'awful', 'poor', 'unhelpful', 'frustrating',
            'disappointed', 'upset', 'angry', 'annoyed', 'worst',
        ]
        
        logger.info("FeedbackAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Process user feedback.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Feedback analysis
        """
        start_time = time.time()
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(context.query)
        
        # Categorize feedback
        category = self._categorize_feedback(context.query)
        
        # Extract satisfaction score if present
        satisfaction = self._extract_satisfaction(context.query)
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "sentiment": sentiment,
                "category": category,
                "satisfaction_score": satisfaction,
                "feedback_text": context.query,
            },
            confidence=0.8,
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of feedback.
        
        Args:
            text: Feedback text
            
        Returns:
            str: Sentiment (positive, negative, neutral)
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for term in self.positive_terms if term in text_lower)
        negative_count = sum(1 for term in self.negative_terms if term in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _categorize_feedback(self, text: str) -> str:
        """
        Categorize feedback type.
        
        Args:
            text: Feedback text
            
        Returns:
            str: Feedback category
        """
        categories = {
            "appreciation": ['thank', 'great', 'good', 'excellent', 'helpful'],
            "complaint": ['bad', 'terrible', 'awful', 'poor', 'problem', 'issue'],
            "suggestion": ['suggest', 'could', 'should', 'improve', 'better'],
            "question": ['what', 'how', 'when', 'where', 'why', 'can'],
            "escalation": ['human', 'agent', 'representative', 'staff', 'person'],
        }
        
        text_lower = text.lower()
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _extract_satisfaction(self, text: str) -> Optional[int]:
        """
        Extract satisfaction score from feedback.
        
        Args:
            text: Feedback text
            
        Returns:
            Optional[int]: Satisfaction score (1-5)
        """
        # Look for explicit ratings
        rating_patterns = [
            r'(\d)\s*(?:out of|/)\s*(?:5|five|10|ten)',
            r'(\d)\s*(?:star|stars)',
            r'rating[:\s]*(\d)',
            r'score[:\s]*(\d)',
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                # Normalize to 1-5
                if score > 5:
                    score = min(5, round(score / 2))
                return score
        
        # Infer from sentiment
        sentiment = self._analyze_sentiment(text)
        if sentiment == "positive":
            return 5
        elif sentiment == "negative":
            return 1
        elif sentiment == "neutral":
            return 3
        
        return None