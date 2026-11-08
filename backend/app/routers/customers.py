"""
app/routers/customers.py
------------------------
Customer list and detail endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.customer_analytics import CustomerAnalyticsService

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("")
def list_customers(
    scenario: str = Query("fintech", description="Business scenario"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filter by status: active, inactive, churned"
    ),
    segment: Optional[str] = Query(None, description="Filter by segment"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a paginated, filterable list of customers."""
    result = CustomerAnalyticsService.get_customers(
        db,
        scenario=scenario,
        skip=skip,
        limit=limit,
        search=search,
        status=status_filter,
        segment=segment,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return result


@router.get("/{customer_id}")
def get_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return detailed information for a single customer."""
    result = CustomerAnalyticsService.get_customer_detail(db, customer_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found",
        )
    return result
