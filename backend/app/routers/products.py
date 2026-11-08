"""
app/routers/products.py
-----------------------
Product usage and feature adoption endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.product_analytics import ProductAnalyticsService

router = APIRouter(prefix="/api/products", tags=["Product Analytics"])


@router.get("/usage")
def product_usage(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return product usage summary, trends, and segment breakdown."""
    summary = ProductAnalyticsService.get_product_summary(db, scenario)
    trend = ProductAnalyticsService.get_usage_trend(db, scenario)
    by_segment = ProductAnalyticsService.get_usage_by_segment(db, scenario)

    return {
        "scenario": scenario,
        "summary": summary,
        "trend": trend,
        "by_segment": by_segment,
    }


@router.get("/features")
def feature_adoption(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return feature-level adoption metrics."""
    features = ProductAnalyticsService.get_feature_adoption(db, scenario)
    return {"scenario": scenario, "features": features}
