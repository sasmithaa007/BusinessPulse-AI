"""
app/schemas/analytics.py
------------------------
Pydantic v2 schemas for dashboard KPI and analytics endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
#  Dashboard summary
# ---------------------------------------------------------------------------


class KPICard(BaseModel):
    """A single KPI metric with optional comparison to a previous period."""

    label: str
    value: float
    formatted_value: str = Field(..., description="Human-readable value, e.g. '₹1.2 M'")
    change_pct: Optional[float] = Field(
        None, description="Percentage change vs previous period"
    )
    trend: Optional[str] = Field(
        None, description="'up' | 'down' | 'flat'"
    )
    unit: Optional[str] = None


class DashboardSummary(BaseModel):
    """High-level KPI cards shown on the main dashboard."""

    business_scenario: str
    period: str
    total_revenue: KPICard
    total_customers: KPICard
    active_customers: KPICard
    churn_rate: KPICard
    avg_transaction_value: KPICard
    success_rate: KPICard


# ---------------------------------------------------------------------------
#  Revenue trend
# ---------------------------------------------------------------------------


class RevenueTrendPoint(BaseModel):
    """Revenue figure for a single time bucket."""

    label: str = Field(..., description="Month or date label, e.g. 'Jan 2024'")
    revenue: float
    transaction_count: int
    avg_value: float


class RevenueTrend(BaseModel):
    """Time-series revenue trend for a scenario."""

    business_scenario: str
    period: str
    data_points: List[RevenueTrendPoint]


# ---------------------------------------------------------------------------
#  Customer trend
# ---------------------------------------------------------------------------


class CustomerTrendPoint(BaseModel):
    """Customer counts for a single time bucket."""

    label: str
    new_customers: int
    churned_customers: int
    active_customers: int
    net_growth: int


class CustomerTrend(BaseModel):
    """Time-series customer acquisition / churn trend."""

    business_scenario: str
    period: str
    data_points: List[CustomerTrendPoint]


# ---------------------------------------------------------------------------
#  Transaction summary
# ---------------------------------------------------------------------------


class TransactionSummary(BaseModel):
    """Aggregate transaction metrics."""

    business_scenario: str
    period: str
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    refunded_transactions: int
    total_volume: float
    success_rate: float
    failure_rate: float
    avg_processing_time_ms: float
    payment_method_breakdown: Dict[str, int]


# ---------------------------------------------------------------------------
#  Product usage summary
# ---------------------------------------------------------------------------


class FeatureUsageStat(BaseModel):
    """Usage statistics for a single feature."""

    feature_name: str
    total_usage: int
    unique_customers: int
    avg_session_duration_minutes: float


class ProductUsageSummary(BaseModel):
    """Aggregate product usage analytics."""

    business_scenario: str
    period: str
    total_sessions: int
    avg_session_duration_minutes: float
    top_features: List[FeatureUsageStat]
    dau: int = Field(..., description="Daily active users (last 24 h)")
    mau: int = Field(..., description="Monthly active users (last 30 days)")


# ---------------------------------------------------------------------------
#  Performance / API summary
# ---------------------------------------------------------------------------


class PerformanceSummary(BaseModel):
    """API performance metrics for the developer-tools scenario."""

    business_scenario: str
    period: str
    total_requests: int
    error_rate: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    top_endpoints: List[Dict[str, Any]]
    error_breakdown: Dict[str, int]


# ---------------------------------------------------------------------------
#  Operations summary
# ---------------------------------------------------------------------------


class OperationsSummary(BaseModel):
    """Operational efficiency metrics."""

    business_scenario: str
    period: str
    total_processes: int
    success_rate: float
    failure_rate: float
    avg_processing_time_seconds: float
    total_operational_cost: float
    cost_by_department: Dict[str, float]


# ---------------------------------------------------------------------------
#  Insight item
# ---------------------------------------------------------------------------


class InsightItem(BaseModel):
    """A single AI-generated or rule-based business insight."""

    id: str = Field(..., description="Unique identifier for the insight")
    category: str = Field(
        ..., description="'revenue' | 'churn' | 'performance' | 'operations' | 'growth'"
    )
    severity: str = Field(..., description="'info' | 'warning' | 'critical' | 'positive'")
    title: str
    description: str
    metric_value: Optional[float] = None
    metric_label: Optional[str] = None
    action_items: List[str] = Field(default_factory=list)
    business_scenario: str
