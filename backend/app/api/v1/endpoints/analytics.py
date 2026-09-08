"""
HealthConnect AI - Analytics Endpoints
=======================================
Analytics and reporting endpoints.

Endpoints:
- GET /analytics/metrics: Get current metrics
- GET /analytics/report: Generate report
- POST /analytics/events: Track event
- GET /analytics/trends: Get trend analysis
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body

from app.api.deps import get_current_admin, get_analytics_service

from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/metrics")
async def get_metrics(
    current_user: dict = Depends(get_current_admin),
    analytics_service = Depends(get_analytics_service),
):
    """
    Get current analytics metrics (admin only).
    """
    metrics = await analytics_service.get_metrics()
    return metrics


@router.get("/report")
async def generate_report(
    period: str = Query(default="daily", pattern="^(daily|weekly|monthly|all_time)$"),
    current_user: dict = Depends(get_current_admin),
    analytics_service = Depends(get_analytics_service),
):
    """
    Generate analytics report (admin only).
    """
    report = await analytics_service.generate_report(period=period)
    return report


@router.post("/events")
async def track_event(
    event_type: str = Body(..., embed=True),
    event_data: Optional[Dict[str, Any]] = Body(default=None, embed=True),
    current_user: dict = Depends(get_current_admin),
    analytics_service = Depends(get_analytics_service),
):
    """
    Track an analytics event (admin only).
    """
    result = await analytics_service.track_event(
        event_type=event_type,
        event_data=event_data,
    )
    return result


@router.get("/trends")
async def get_trends(
    metric: str = Query(default="conversations", description="Metric to analyze"),
    period: str = Query(default="7d", description="Time period"),
    current_user: dict = Depends(get_current_admin),
    analytics_service = Depends(get_analytics_service),
):
    """
    Get trend analysis (admin only).
    """
    metrics = await analytics_service.get_metrics()
    
    # Extract trend data
    trends = {
        "metric": metric,
        "period": period,
        "data_points": [],
    }
    
    if metric == "conversations":
        trends["data_points"] = [
            {"date": date, "count": count}
            for date, count in sorted(metrics.get("daily_activity", {}).items())
        ]
    elif metric == "hourly":
        trends["data_points"] = [
            {"hour": hour, "count": count}
            for hour, count in sorted(metrics.get("hourly_activity", {}).items())
        ]
    
    return trends