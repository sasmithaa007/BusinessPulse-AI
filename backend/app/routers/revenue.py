"""
app/routers/revenue.py
----------------------
Revenue analytics endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.revenue_analytics import RevenueAnalyticsService

router = APIRouter(prefix="/api/revenue", tags=["Revenue Analytics"])


@router.get("/summary")
def revenue_summary(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return revenue summary including totals, by-segment, and by-plan breakdowns."""
    summary = RevenueAnalyticsService.get_revenue_summary(db, scenario)
    by_segment = RevenueAnalyticsService.get_revenue_by_segment(db, scenario)
    by_plan = RevenueAnalyticsService.get_revenue_by_plan(db, scenario)

    return {
        "scenario": scenario,
        "summary": summary,
        "by_segment": by_segment,
        "by_plan": by_plan,
    }


@router.get("/trend")
def revenue_trend(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return monthly revenue trend data."""
    trend = RevenueAnalyticsService.get_revenue_trend(db, scenario)
    return {"scenario": scenario, "trend": trend}


@router.get("/leakage")
def revenue_leakage(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return revenue leakage analysis (failed transactions, refunds, etc.)."""
    leakage = RevenueAnalyticsService.get_revenue_leakage(db, scenario)
    return {"scenario": scenario, "leakage": leakage}
