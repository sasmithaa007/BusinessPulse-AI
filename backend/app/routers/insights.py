"""
app/routers/insights.py
-----------------------
AI-generated business insights endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.insight_engine import InsightEngine

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("")
def get_insights(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return AI-generated / rule-based business insights for the given scenario."""
    insights = InsightEngine.get_insights(db, scenario)
    return {"scenario": scenario, "insights": insights}
