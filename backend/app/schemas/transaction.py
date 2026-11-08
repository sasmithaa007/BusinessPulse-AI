"""
app/schemas/transaction.py
--------------------------
Pydantic v2 schemas for transaction endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TransactionOut(BaseModel):
    """Full representation of a single transaction record."""

    id: int
    customer_id: int
    transaction_code: str
    transaction_date: datetime
    amount: float
    currency: str
    status: str
    payment_method: str
    failure_reason: Optional[str] = None
    gateway: str
    processing_time_ms: int
    business_scenario: str

    model_config = {"from_attributes": True}


class TransactionList(BaseModel):
    """Paginated list of transactions."""

    total: int = Field(..., description="Total matching transactions")
    page: int
    page_size: int
    items: List[TransactionOut]


class TransactionSummary(BaseModel):
    """Aggregate transaction statistics."""

    business_scenario: str
    period: str
    total_transactions: int
    successful: int
    failed: int
    pending: int
    refunded: int
    total_volume: float
    avg_amount: float
    success_rate: float
    avg_processing_time_ms: float


class FailureReasonBreakdown(BaseModel):
    """Count of failures grouped by reason."""

    reason: str
    count: int
    percentage: float


class PaymentMethodBreakdown(BaseModel):
    """Transaction counts per payment method."""

    method: str
    count: int
    volume: float
    success_rate: float


class FailureAnalysis(BaseModel):
    """Detailed failure analysis for a scenario / period."""

    business_scenario: str
    period: str
    total_failures: int
    failure_rate: float
    reasons: List[FailureReasonBreakdown]
    by_payment_method: List[PaymentMethodBreakdown]
    top_failing_gateways: List[Dict[str, float]]
