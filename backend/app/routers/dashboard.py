"""
app/routers/dashboard.py
------------------------
Dashboard summary and trend endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.customer_analytics import CustomerAnalyticsService
from app.services.revenue_analytics import RevenueAnalyticsService
from app.services.churn_analytics import ChurnAnalyticsService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return top-level KPI summary for the dashboard.

    Aggregates customer, revenue, and churn data into a single response.
    """
    customer_summary = CustomerAnalyticsService.get_customer_summary(db, scenario)
    revenue_summary = RevenueAnalyticsService.get_revenue_summary(db, scenario)
    churn_stats = ChurnAnalyticsService.get_churn_stats(db, scenario)

    return {
        "scenario": scenario,
        "customers": customer_summary,
        "revenue": revenue_summary,
        "churn": churn_stats,
    }


@router.get("/revenue-trend")
def revenue_trend(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return monthly revenue trend data for charting."""
    trend = RevenueAnalyticsService.get_revenue_trend(db, scenario)
    return {"scenario": scenario, "trend": trend}


@router.get("/customer-trend")
def customer_trend(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return monthly customer acquisition / churn trend."""
    customer_summary = CustomerAnalyticsService.get_customer_summary(db, scenario)
    churn_trend = ChurnAnalyticsService.get_churn_trend(db, scenario)

    return {
        "scenario": scenario,
        "summary": customer_summary,
        "trend": churn_trend,
    }
