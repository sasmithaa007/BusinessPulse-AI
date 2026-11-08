"""
app/routers/segmentation.py
----------------------------
Customer segmentation and RFM analysis endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.segmentation import SegmentationService

router = APIRouter(prefix="/api/customers/segments", tags=["Segmentation"])


@router.get("")
def segment_overview(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return customer segment distribution and value analysis."""
    distribution = SegmentationService.get_segment_distribution(db, scenario)
    value = SegmentationService.get_segment_value(db, scenario)

    return {
        "scenario": scenario,
        "distribution": distribution,
        "value": value,
    }


@router.get("/rfm")
def rfm_analysis(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return RFM (Recency, Frequency, Monetary) analysis."""
    rfm = SegmentationService.get_rfm_analysis(db, scenario)
    return {"scenario": scenario, "rfm": rfm}
