"""
app/routers/retention.py
------------------------
Retention analytics endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.retention_analytics import RetentionAnalyticsService

router = APIRouter(prefix="/api/customers/retention", tags=["Retention Analytics"])


@router.get("")
def retention_overview(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return retention statistics and monthly retention data."""
    stats = RetentionAnalyticsService.get_retention_stats(db, scenario)
    monthly = RetentionAnalyticsService.get_monthly_retention(db, scenario)

    return {
        "scenario": scenario,
        "stats": stats,
        "monthly_retention": monthly,
    }


@router.get("/cohort")
def retention_cohort(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return cohort-based retention analysis."""
    cohort = RetentionAnalyticsService.get_cohort_retention(db, scenario)
    return {"scenario": scenario, "cohort": cohort}


@router.get("/by-segment")
def retention_by_segment(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return retention rates broken down by customer segment."""
    by_segment = RetentionAnalyticsService.get_retention_by_segment(db, scenario)
    return {"scenario": scenario, "by_segment": by_segment}
