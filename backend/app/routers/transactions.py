"""
app/routers/transactions.py
----------------------------
Transaction analytics endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.transaction_analytics import TransactionAnalyticsService

router = APIRouter(prefix="/api/transactions", tags=["Transaction Analytics"])


@router.get("")
def list_transactions(
    scenario: str = Query("fintech", description="Business scenario"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filter by status: success, failed, pending"
    ),
    payment_method: Optional[str] = Query(
        None, description="Filter by payment method"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date filter (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date filter (YYYY-MM-DD)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a paginated list of transactions with optional filters."""
    result = TransactionAnalyticsService.get_transactions_paginated(
        db,
        scenario=scenario,
        skip=skip,
        limit=limit,
        status=status_filter,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
    )
    return result


@router.get("/summary")
def transaction_summary(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregate transaction statistics."""
    summary = TransactionAnalyticsService.get_transaction_summary(db, scenario)
    trend = TransactionAnalyticsService.get_transaction_trend(db, scenario)

    return {
        "scenario": scenario,
        "summary": summary,
        "trend": trend,
    }


@router.get("/failures")
def failure_analysis(
    scenario: str = Query("fintech", description="Business scenario"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return detailed failure analysis: reasons, methods, and gateways."""
    analysis = TransactionAnalyticsService.get_failure_analysis(db, scenario)
    return {"scenario": scenario, "analysis": analysis}
