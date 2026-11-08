"""
app/routers/operations.py
-------------------------
Operational analytics endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.operational_analytics import OperationalAnalyticsService

router = APIRouter(prefix="/api/operations", tags=["Operational Analytics"])


@router.get("/summary")
def operations_summary(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return operational efficiency summary with costs and process breakdown."""
    summary = OperationalAnalyticsService.get_operations_summary(db, scenario)
    cost_trend = OperationalAnalyticsService.get_cost_trend(db, scenario)
    breakdown = OperationalAnalyticsService.get_process_breakdown(db, scenario)

    return {
        "scenario": scenario,
        "summary": summary,
        "cost_trend": cost_trend,
        "process_breakdown": breakdown,
    }


@router.get("/bottlenecks")
def bottlenecks(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return operational bottleneck analysis."""
    bottleneck_data = OperationalAnalyticsService.get_bottlenecks(db, scenario)
    return {"scenario": scenario, "bottlenecks": bottleneck_data}
