"""
HealthConnect AI - Analytics MCP Server (STATEFUL)
===================================================
Stateful MCP server with Redis-backed state persistence.
"""

import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import deque

from app.mcp.mcp_server import BaseMCPServer, MCPTool, MCPToolResult, MCPToolStatus

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AnalyticsMCPServer(BaseMCPServer):
    """STATEFUL Analytics MCP Server with Redis-backed state."""
    
    STATE_KEY = "mcp:analytics:state"
    STATE_TTL = 86400
    MAX_EVENTS = 10000
    MAX_RESPONSE_TIMES = 1000
    
    def __init__(self, config=None):
        super().__init__("analytics", config)
        self._redis_client = None
        self._redis_available = False
        self._memory_state = {
            "events": [],
            "total_events": 0,
            "event_type_counts": {},
            "hourly_activity": {},
            "daily_activity": {},
            "response_times": [],
            "last_updated": None,
            "initialized_at": datetime.now(timezone.utc).isoformat(),
        }
        self._event_queue = deque(maxlen=1000)
        self._register_tools()
    
    def _register_tools(self):
        self.register_tools([
            MCPTool(name="track_event", description="Track event", handler=self.track_event, parameters={"event_type": {"type": "string"}, "event_data": {"type": "object"}}, timeout_seconds=5.0),
            MCPTool(name="get_metrics", description="Get metrics", handler=self.get_metrics, parameters={}, timeout_seconds=5.0, requires_auth=True),
            MCPTool(name="generate_report", description="Generate report", handler=self.generate_report, parameters={"period": {"type": "string", "default": "daily"}}, timeout_seconds=15.0, requires_auth=True),
            MCPTool(name="get_trends", description="Get trends", handler=self.get_trends, parameters={"metric": {"type": "string", "default": "events"}, "hours": {"type": "integer", "default": 24}}, timeout_seconds=10.0, requires_auth=True),
            MCPTool(name="reset_state", description="Reset state", handler=self.reset_state, parameters={}, timeout_seconds=5.0, requires_auth=True),
        ])
    
    async def initialize(self):
        try:
            import redis.asyncio as redis
            self._redis_client = redis.from_url(settings.redis.URL, password=settings.redis.PASSWORD or None, db=settings.redis.DB, decode_responses=True)
            await self._redis_client.ping()
            self._redis_available = True
            await self._load_state_from_redis()
            logger.info("Analytics MCP Server: Redis state initialized")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}. Using in-memory fallback.")
            self._redis_client = None
            self._redis_available = False
        self._initialized = True
    
    async def close(self):
        await self._save_state()
        if self._redis_client:
            await self._redis_client.close()
        self._initialized = False
    
    async def _get_state(self):
        if self._redis_available and self._redis_client:
            try:
                state_json = await self._redis_client.get(self.STATE_KEY)
                if state_json:
                    return json.loads(state_json)
            except Exception as e:
                logger.error(f"Failed to get state: {e}")
        return self._memory_state
    
    async def _save_state(self):
        self._memory_state["last_updated"] = datetime.now(timezone.utc).isoformat()
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.set(self.STATE_KEY, json.dumps(self._memory_state, default=str), ex=self.STATE_TTL)
            except Exception as e:
                logger.error(f"Failed to save state: {e}")
    
    async def _load_state_from_redis(self):
        if self._redis_available and self._redis_client:
            try:
                state_json = await self._redis_client.get(self.STATE_KEY)
                if state_json:
                    self._memory_state.update(json.loads(state_json))
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
    
    async def track_event(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        event_data = event_data or {}
        timestamp = datetime.now(timezone.utc)
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": timestamp.isoformat(),
            "hour": timestamp.hour,
            "date": timestamp.date().isoformat()
        }
        
        state = await self._get_state()
        events = state.get("events", [])
        events.append(event)
        if len(events) > self.MAX_EVENTS:
            events = events[-self.MAX_EVENTS:]
        state["events"] = events
        state["total_events"] = state.get("total_events", 0) + 1
        
        event_type_counts = state.get("event_type_counts", {})
        event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        state["event_type_counts"] = event_type_counts
        
        hourly = state.get("hourly_activity", {})
        hour_key = timestamp.strftime("%Y-%m-%d:%H")
        hourly[hour_key] = hourly.get(hour_key, 0) + 1
        state["hourly_activity"] = hourly
        
        daily = state.get("daily_activity", {})
        daily[timestamp.date().isoformat()] = daily.get(timestamp.date().isoformat(), 0) + 1
        state["daily_activity"] = daily
        
        self._memory_state = state
        await self._save_state()
        self._event_queue.append(event)
        
        return {
            "status": "tracked",
            "event_type": event_type,
            "event_id": event["event_id"],
            "total_events": state["total_events"],
            "state_storage": "redis" if self._redis_available else "memory"
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        state = await self._get_state()
        response_times = state.get("response_times", [])
        return {
            "total_events": state.get("total_events", 0),
            "event_type_counts": state.get("event_type_counts", {}),
            "hourly_activity": state.get("hourly_activity", {}),
            "daily_activity": state.get("daily_activity", {}),
            "average_response_time_ms": (sum(response_times) / len(response_times) if response_times else 0),
            "p95_response_time_ms": self._calculate_percentile(response_times, 95),
            "recent_events": state.get("events", [])[-10:],
            "state_storage": "redis" if self._redis_available else "memory",
            "last_updated": state.get("last_updated"),
            "initialized_at": state.get("initialized_at")
        }
    
    async def generate_report(self, period: str = "daily") -> Dict[str, Any]:
        state = await self._get_state()
        metrics = await self.get_metrics()
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": period,
            "metrics": metrics,
            "state_summary": {
                "total_events": state.get("total_events", 0),
                "event_types": len(state.get("event_type_counts", {})),
                "active_hours": len(state.get("hourly_activity", {})),
                "active_days": len(state.get("daily_activity", {}))
            }
        }
    
    async def get_trends(self, metric: str = "events", hours: int = 24) -> Dict[str, Any]:
        state = await self._get_state()
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=hours)
        trends = []
        if metric == "events":
            hourly = state.get("hourly_activity", {})
            for hour_key, count in sorted(hourly.items()):
                try:
                    hour_dt = datetime.strptime(hour_key, "%Y-%m-%d:%H").replace(tzinfo=timezone.utc)
                    if hour_dt >= cutoff:
                        trends.append({"timestamp": hour_dt.isoformat(), "count": count})
                except ValueError:
                    continue
        elif metric == "daily":
            daily = state.get("daily_activity", {})
            for date_key, count in sorted(daily.items()):
                trends.append({"date": date_key, "count": count})
        return {
            "metric": metric,
            "hours": hours,
            "data_points": trends,
            "total_points": len(trends),
            "state_storage": "redis" if self._redis_available else "memory"
        }
    
    async def reset_state(self) -> Dict[str, Any]:
        self._memory_state = {
            "events": [],
            "total_events": 0,
            "event_type_counts": {},
            "hourly_activity": {},
            "daily_activity": {},
            "response_times": [],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "initialized_at": datetime.now(timezone.utc).isoformat()
        }
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.delete(self.STATE_KEY)
            except Exception as e:
                logger.error(f"Failed to clear Redis: {e}")
        return {"status": "reset", "state_storage": "redis" if self._redis_available else "memory"}
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = min(int(len(sorted_values) * percentile / 100), len(sorted_values) - 1)
        return sorted_values[index]
    
    async def track_response_time(self, response_time_ms: float) -> None:
        state = await self._get_state()
        response_times = state.get("response_times", [])
        response_times.append(response_time_ms)
        if len(response_times) > self.MAX_RESPONSE_TIMES:
            response_times = response_times[-self.MAX_RESPONSE_TIMES:]
        state["response_times"] = response_times
        self._memory_state = state
        await self._save_state()
    
    def get_state_status(self) -> Dict[str, Any]:
        return {
            "server_name": self.server_name,
            "state_type": "stateful",
            "redis_available": self._redis_available,
            "state_key": self.STATE_KEY,
            "state_ttl": self.STATE_TTL,
            "max_events": self.MAX_EVENTS,
            "max_response_times": self.MAX_RESPONSE_TIMES,
            "current_memory_events": len(self._memory_state.get("events", [])),
            "queue_size": len(self._event_queue)
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        base_stats = super().get_stats()
        base_stats.update(self.get_state_status())
        return base_stats
