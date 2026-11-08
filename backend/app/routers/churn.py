"""
app/routers/churn.py
--------------------
Churn analytics endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.churn_analytics import ChurnAnalyticsService
from app.services.churn_prediction import ChurnPredictionService

router = APIRouter(prefix="/api/customers/churn", tags=["Churn Analytics"])


@router.get("")
def churn_overview(
    scenario: str = Query("fintech", description="Business scenario"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return churn statistics including rate, risk distribution, and segment breakdown."""
    stats = ChurnAnalyticsService.get_churn_stats(
        db, scenario, start_date=start_date, end_date=end_date
    )
    by_segment = ChurnAnalyticsService.get_churn_by_segment(db, scenario)
    risk_distribution = ChurnAnalyticsService.get_churn_risk_distribution(db, scenario)

    return {
        "scenario": scenario,
        "stats": stats,
        "by_segment": by_segment,
        "risk_distribution": risk_distribution,
    }


@router.get("/trend")
def churn_trend(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return monthly churn trend data."""
    trend = ChurnAnalyticsService.get_churn_trend(db, scenario)
    return {"scenario": scenario, "trend": trend}


@router.get("/prediction")
def churn_prediction(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run the churn prediction model and return risk scores."""
    predictions = ChurnPredictionService.train_and_predict(db, scenario)
    return {"scenario": scenario, "predictions": predictions}
