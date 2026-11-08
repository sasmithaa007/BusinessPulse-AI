"""
Pydantic schemas for BusinessPulse AI API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Auth ───────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "analyst"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── Customer ────────────────────────────────────────────────────────────────

class CustomerOut(BaseModel):
    id: int
    scenario: str
    name: str
    email: Optional[str]
    segment: Optional[str]
    status: Optional[str]
    subscription_plan: Optional[str]
    lifetime_value: Optional[float]
    churn_risk_score: Optional[float]
    signup_date: Optional[datetime]
    last_activity_date: Optional[datetime]

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    total: int
    active: int
    inactive: int
    churned: int


class PaginatedCustomers(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[CustomerOut]


# ─── Transaction ─────────────────────────────────────────────────────────────

class TransactionOut(BaseModel):
    id: int
    scenario: str
    customer_id: Optional[int]
    amount: float
    status: str
    payment_method: Optional[str]
    failure_reason: Optional[str]
    transaction_date: Optional[datetime]

    class Config:
        from_attributes = True


class TransactionSummary(BaseModel):
    total_count: int
    success_count: int
    failed_count: int
    total_amount: float
    success_amount: float
    failed_amount: float
    success_rate: float
    failure_rate: float
    avg_transaction_value: float


class PaginatedTransactions(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[TransactionOut]


# ─── Revenue ─────────────────────────────────────────────────────────────────

class RevenueSummary(BaseModel):
    total_revenue: float
    mrr: float
    arr: float
    failed_billing: float
    revenue_growth: float


class RevenueLeakage(BaseModel):
    failed_amount: float
    recoverable_amount: float
    total_failed_transactions: int


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    customer_summary: CustomerSummary
    revenue_summary: RevenueSummary
    transaction_summary: TransactionSummary
    churn_rate: float
    retention_rate: float
    top_insights: List[Dict[str, Any]]


# ─── Insight ─────────────────────────────────────────────────────────────────

class InsightItem(BaseModel):
    business_problem: str
    metric: str
    observed_value: float
    threshold: float
    explanation: str
    recommended_action: str
    priority: str          # high / medium / low
    evidence_level: str    # confirmed / correlation / hypothesis


# ─── Churn ───────────────────────────────────────────────────────────────────

class ChurnStats(BaseModel):
    churn_rate: float
    churned_count: int
    active_count: int
    inactive_count: int
    total: int


class ChurnSegment(BaseModel):
    segment: str
    churned: int
    total: int
    churn_rate: float


class ChurnTrendPoint(BaseModel):
    month: str
    churned: int
    total: int
    churn_rate: float


class ChurnRiskDistribution(BaseModel):
    low: int
    medium: int
    high: int


# ─── Retention ───────────────────────────────────────────────────────────────

class RetentionStats(BaseModel):
    retention_rate: float
    active_count: int
    non_churned_count: int


class MonthlyRetention(BaseModel):
    month: str
    retention_rate: float
    active: int
    total: int


class CohortRetention(BaseModel):
    cohort_month: str
    cohort_size: int
    retention_1m: float
    retention_3m: float
    retention_6m: float


class SegmentRetention(BaseModel):
    segment: str
    retention_rate: float
    active: int
    total: int


# ─── Product ─────────────────────────────────────────────────────────────────

class ProductSummary(BaseModel):
    active_users: int
    total_usage_events: int
    top_features: List[Dict[str, Any]]


class FeatureAdoption(BaseModel):
    feature_name: str
    unique_users: int
    total_customers: int
    adoption_rate: float


# ─── Performance ─────────────────────────────────────────────────────────────

class PerformanceSummary(BaseModel):
    total_requests: int
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float


class EndpointPerformance(BaseModel):
    endpoint: str
    method: str
    request_count: int
    avg_response_time: float
    p95_response_time: float
    error_rate: float


# ─── Operations ──────────────────────────────────────────────────────────────

class OperationsSummary(BaseModel):
    total_processes: int
    success_count: int
    failed_count: int
    avg_processing_time: float
    total_cost: float
    success_rate: float


class ProcessBottleneck(BaseModel):
    process_name: str
    avg_processing_time: float
    count: int


# ─── Segmentation ────────────────────────────────────────────────────────────

class SegmentDistribution(BaseModel):
    segment: str
    count: int
    percentage: float


class SegmentValue(BaseModel):
    segment: str
    avg_lifetime_value: float
    total_revenue: float
    customer_count: int


class RFMCustomer(BaseModel):
    customer_id: int
    name: str
    segment: str
    recency_days: int
    frequency: int
    monetary: float
    r_score: int
    f_score: int
    m_score: int
    rfm_score: int
    rfm_label: str


# ─── Dataset ─────────────────────────────────────────────────────────────────

class DatasetMeta(BaseModel):
    id: str
    filename: str
    rows: int
    columns: List[str]
    uploaded_at: str


class DatasetPreview(BaseModel):
    id: str
    filename: str
    columns: List[str]
    rows: int
    preview: List[Dict[str, Any]]


# ─── Generic Response ────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = "OK"
