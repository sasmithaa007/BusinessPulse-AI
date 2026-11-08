"""
app/schemas/customer.py
-----------------------
Pydantic v2 schemas for customer list, detail, and analytics endpoints.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class CustomerOut(BaseModel):
    """Full representation of a customer record."""

    id: int
    customer_code: str
    name: str
    email: str
    customer_type: str
    business_scenario: str
    signup_date: date
    country: str
    status: str
    segment: str
    lifetime_value: float
    churn_risk_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerList(BaseModel):
    """Paginated list of customers."""

    total: int = Field(..., description="Total number of matching customers")
    page: int = Field(..., description="Current page (1-based)")
    page_size: int = Field(..., description="Number of items per page")
    items: List[CustomerOut]


class CustomerFilters(BaseModel):
    """Query filters for the customer list endpoint."""

    business_scenario: Optional[str] = None
    status: Optional[str] = None
    segment: Optional[str] = None
    customer_type: Optional[str] = None
    country: Optional[str] = None
    min_ltv: Optional[float] = None
    max_ltv: Optional[float] = None
    min_churn_risk: Optional[float] = None
    max_churn_risk: Optional[float] = None


# ---------------------------------------------------------------------------
#  Analytics summaries
# ---------------------------------------------------------------------------


class ChurnStats(BaseModel):
    """Churn rate statistics for a given scenario / period."""

    business_scenario: str
    total_customers: int
    churned_customers: int
    churn_rate: float = Field(..., description="Fraction 0–1")
    high_risk_customers: int = Field(
        ..., description="Customers with churn_risk_score > 0.7"
    )
    avg_churn_risk: float


class RetentionStats(BaseModel):
    """Retention metrics for a given scenario."""

    business_scenario: str
    period_label: str
    retained_customers: int
    new_customers: int
    total_active: int
    retention_rate: float = Field(..., description="Fraction 0–1")


class SegmentDistribution(BaseModel):
    """Customer count per segment."""

    segment: str
    count: int
    percentage: float


class SegmentStats(BaseModel):
    """Segment breakdown for a business scenario."""

    business_scenario: str
    total: int
    distribution: List[SegmentDistribution]
