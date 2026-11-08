"""
app/routers/performance.py
--------------------------
API performance analytics endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.performance_analytics import PerformanceAnalyticsService

router = APIRouter(prefix="/api/performance", tags=["Performance Analytics"])


@router.get("/summary")
def performance_summary(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return API performance summary with response times and error rates."""
    summary = PerformanceAnalyticsService.get_performance_summary(db, scenario)
    slow = PerformanceAnalyticsService.get_slow_endpoints(db, scenario, threshold_ms=1000)
    errors = PerformanceAnalyticsService.get_error_distribution(db, scenario)

    return {
        "scenario": scenario,
        "summary": summary,
        "slow_endpoints": slow,
        "error_distribution": errors,
    }


@router.get("/endpoints")
def endpoint_performance(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return per-endpoint performance breakdown."""
    endpoints = PerformanceAnalyticsService.get_endpoint_performance(db, scenario)
    return {"scenario": scenario, "endpoints": endpoints}
