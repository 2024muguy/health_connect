"""
HealthConnect AI - Analytics Service
=====================================
Business logic for analytics tracking.

Features:
- Event tracking
- Metrics collection
- Report generation
- Trend analysis
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter

from app.mcp.servers.analytics_server import AnalyticsMCPServer

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AnalyticsService:
    """
    Analytics Service.
    Tracks and analyzes system performance.
    """
    
    def __init__(self):
        self.analytics_server = AnalyticsMCPServer()
        self._metrics: Dict[str, Any] = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_appointments": 0,
            "total_escalations": 0,
            "total_no_shows": 0,
            "intent_counts": Counter(),
            "safety_counts": Counter(),
            "hourly_activity": Counter(),
            "daily_activity": Counter(),
            "response_times": [],
        }
        logger.info("AnalyticsService initialized")
    
    async def track_event(
        self,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track an analytics event.
        
        Args:
            event_type: Event type
            event_data: Event data
            
        Returns:
            Dict: Tracking result
        """
        result = await self.analytics_server.track_event(event_type, event_data)
        
        # Update internal metrics
        self._update_metrics(event_type, event_data)
        
        return result
    
    def _update_metrics(
        self,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update internal metrics"""
        event_data = event_data or {}
        
        if event_type == "conversation_started":
            self._metrics["total_conversations"] += 1
        elif event_type == "message_sent":
            self._metrics["total_messages"] += 1
        elif event_type == "appointment_booked":
            self._metrics["total_appointments"] += 1
        elif event_type == "escalation_created":
            self._metrics["total_escalations"] += 1
        elif event_type == "no_show_recorded":
            self._metrics["total_no_shows"] += 1
        
        # Track intent
        intent = event_data.get("intent")
        if intent:
            self._metrics["intent_counts"][intent] += 1
        
        # Track safety category
        safety_category = event_data.get("safety_category")
        if safety_category:
            self._metrics["safety_counts"][safety_category] += 1
        
        # Track hourly activity
        current_hour = datetime.now(timezone.utc).hour
        self._metrics["hourly_activity"][current_hour] += 1
        
        # Track daily activity
        current_date = datetime.now(timezone.utc).date().isoformat()
        self._metrics["daily_activity"][current_date] += 1
    
    async def track_response_time(self, response_time_ms: float) -> None:
        """Track response time"""
        self._metrics["response_times"].append(response_time_ms)
        
        # Keep last 1000
        if len(self._metrics["response_times"]) > 1000:
            self._metrics["response_times"] = self._metrics["response_times"][-1000:]
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        response_times = self._metrics["response_times"]
        
        return {
            "total_conversations": self._metrics["total_conversations"],
            "total_messages": self._metrics["total_messages"],
            "total_appointments": self._metrics["total_appointments"],
            "total_escalations": self._metrics["total_escalations"],
            "total_no_shows": self._metrics["total_no_shows"],
            "no_show_rate": self._calculate_no_show_rate(),
            "top_intents": dict(self._metrics["intent_counts"].most_common(10)),
            "safety_categories": dict(self._metrics["safety_counts"]),
            "average_response_time_ms": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "p95_response_time_ms": self._calculate_percentile(response_times, 95),
            "hourly_activity": dict(self._metrics["hourly_activity"]),
            "daily_activity": dict(self._metrics["daily_activity"]),
        }
    
    def _calculate_no_show_rate(self) -> float:
        """Calculate no-show rate"""
        total = self._metrics["total_appointments"]
        if total == 0:
            return 0.0
        
        return (self._metrics["total_no_shows"] / total) * 100
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = min(int(len(sorted_values) * percentile / 100), len(sorted_values) - 1)
        return sorted_values[index]
    
    async def generate_report(self, period: str = "daily") -> Dict[str, Any]:
        """
        Generate analytics report.
        
        Args:
            period: Report period (daily, weekly, monthly)
            
        Returns:
            Dict: Report
        """
        metrics = await self.get_metrics()
        
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": period,
            "metrics": metrics,
        }
    
    async def generate_daily_reports(self) -> Dict[str, Any]:
        """Generate daily report (for Celery task)"""
        return await self.generate_report("daily")
    
    async def reset_metrics(self) -> None:
        """Reset all metrics"""
        self._metrics = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_appointments": 0,
            "total_escalations": 0,
            "total_no_shows": 0,
            "intent_counts": Counter(),
            "safety_counts": Counter(),
            "hourly_activity": Counter(),
            "daily_activity": Counter(),
            "response_times": [],
        }
        logger.info("Analytics metrics reset")