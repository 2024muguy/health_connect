"""
HealthConnect AI - Analytics Agent
===================================
Tracks and analyzes system performance metrics.

Features:
- Performance tracking
- Usage statistics
- Trend analysis
- Report generation
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from collections import Counter

from app.agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentResult,
    AgentStatus,
    AgentType,
)

from config.logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsAgent(BaseAgent):
    """
    Analytics Agent.
    Tracks and analyzes system performance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(AgentType.ANALYTICS, config)
        
        # In-memory metrics store
        self._metrics = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_escalations": 0,
            "total_emergencies": 0,
            "intent_counts": Counter(),
            "safety_category_counts": Counter(),
            "hourly_activity": Counter(),
            "average_response_times": [],
        }
        
        logger.info("AnalyticsAgent initialized")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Track analytics for conversation.
        
        Args:
            context: Agent context
            
        Returns:
            AgentResult: Analytics tracking result
        """
        start_time = time.time()
        
        # Update metrics
        self._update_metrics(context)
        
        return AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            output={
                "tracked": True,
                "conversation_id": context.conversation_id,
                "metrics_snapshot": self.get_metrics_snapshot(),
            },
            confidence=1.0,
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    
    def _update_metrics(self, context: AgentContext) -> None:
        """Update internal metrics"""
        self._metrics["total_conversations"] += 1
        self._metrics["total_messages"] += len(context.history) + 1
        
        # Track intent
        if context.intent:
            self._metrics["intent_counts"][context.intent] += 1
        
        # Track safety category
        safety_category = context.safety_flags.get("safety_category", "unknown")
        self._metrics["safety_category_counts"][safety_category] += 1
        
        # Track hourly activity
        current_hour = datetime.now(timezone.utc).hour
        self._metrics["hourly_activity"][current_hour] += 1
    
    def track_response_time(self, response_time_ms: float) -> None:
        """Track response time"""
        self._metrics["average_response_times"].append(response_time_ms)
        
        # Keep only last 1000
        if len(self._metrics["average_response_times"]) > 1000:
            self._metrics["average_response_times"] = \
                self._metrics["average_response_times"][-1000:]
    
    def track_escalation(self) -> None:
        """Track escalation event"""
        self._metrics["total_escalations"] += 1
    
    def track_emergency(self) -> None:
        """Track emergency event"""
        self._metrics["total_emergencies"] += 1
    
    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        response_times = self._metrics["average_response_times"]
        
        return {
            "total_conversations": self._metrics["total_conversations"],
            "total_messages": self._metrics["total_messages"],
            "total_escalations": self._metrics["total_escalations"],
            "total_emergencies": self._metrics["total_emergencies"],
            "top_intents": dict(self._metrics["intent_counts"].most_common(10)),
            "safety_categories": dict(self._metrics["safety_category_counts"]),
            "average_response_time_ms": (
                sum(response_times) / len(response_times)
                if response_times else 0
            ),
            "p95_response_time_ms": self._calculate_percentile(response_times, 95),
            "hourly_activity": dict(self._metrics["hourly_activity"]),
        }
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        index = min(index, len(sorted_values) - 1)
        
        return sorted_values[index]
    
    async def generate_report(self) -> Dict[str, Any]:
        """
        Generate analytics report.
        
        Returns:
            Dict: Analytics report
        """
        snapshot = self.get_metrics_snapshot()
        
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": "all_time",
            **snapshot,
        }
        
        return report
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""
        self._metrics = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_escalations": 0,
            "total_emergencies": 0,
            "intent_counts": Counter(),
            "safety_category_counts": Counter(),
            "hourly_activity": Counter(),
            "average_response_times": [],
        }
        logger.info("Analytics metrics reset")