"""
app/routers/reports.py
----------------------
Report export endpoint — generates CSV downloads for various report types.
"""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.services.customer_analytics import CustomerAnalyticsService
from app.services.revenue_analytics import RevenueAnalyticsService
from app.services.transaction_analytics import TransactionAnalyticsService
from app.services.product_analytics import ProductAnalyticsService
from app.services.performance_analytics import PerformanceAnalyticsService

router = APIRouter(prefix="/api/reports", tags=["Reports"])

VALID_REPORT_TYPES = {
    "business_performance",
    "customer_analytics",
    "revenue",
    "transactions",
    "products",
}


def _dict_list_to_csv(rows: List[Dict[str, Any]]) -> str:
    """Convert a list of flat dicts into a CSV string."""
    if not rows:
        return ""

    output = io.StringIO()
    # Gather all keys across all rows to handle sparse dicts
    fieldnames: List[str] = []
    seen: set = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        # Flatten any nested dicts/lists to their string representation
        flat_row = {}
        for k, v in row.items():
            if isinstance(v, (dict, list)):
                flat_row[k] = str(v)
            else:
                flat_row[k] = v
        writer.writerow(flat_row)

    return output.getvalue()


def _flatten_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten a nested dict into a single-level dict with dotted keys."""
    flat: Dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten_dict(value, full_key))
        elif isinstance(value, list):
            flat[full_key] = str(value)
        else:
            flat[full_key] = value
    return flat


def _build_business_performance_report(db: Session, scenario: str) -> str:
    """Build a CSV combining customer summary, revenue, and transaction data."""
    customer_summary = CustomerAnalyticsService.get_customer_summary(db, scenario)
    revenue_summary = RevenueAnalyticsService.get_revenue_summary(db, scenario)
    revenue_trend = RevenueAnalyticsService.get_revenue_trend(db, scenario)

    # Build a combined summary row
    summary_row = {"report_type": "business_performance", "scenario": scenario}
    if isinstance(customer_summary, dict):
        summary_row.update(_flatten_dict(customer_summary, "customer"))
    if isinstance(revenue_summary, dict):
        summary_row.update(_flatten_dict(revenue_summary, "revenue"))

    rows: List[Dict[str, Any]] = [summary_row]

    # Append trend data if it's a list
    if isinstance(revenue_trend, list):
        for item in revenue_trend:
            if isinstance(item, dict):
                row = {"report_type": "revenue_trend", "scenario": scenario}
                row.update(item)
                rows.append(row)

    return _dict_list_to_csv(rows)


def _build_customer_analytics_report(db: Session, scenario: str) -> str:
    """Build a CSV of customer data."""
    result = CustomerAnalyticsService.get_customers(
        db, scenario=scenario, skip=0, limit=10000,
        search=None, status=None, segment=None,
        sort_by="created_at", sort_order="desc",
    )

    if isinstance(result, dict) and "items" in result:
        rows = result["items"]
    elif isinstance(result, list):
        rows = result
    else:
        rows = [result] if isinstance(result, dict) else []

    # Convert ORM objects to dicts if needed
    processed_rows: List[Dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            processed_rows.append(row)
        elif hasattr(row, "__dict__"):
            d = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
            processed_rows.append(d)

    return _dict_list_to_csv(processed_rows)


def _build_revenue_report(db: Session, scenario: str) -> str:
    """Build a CSV of revenue trend data."""
    summary = RevenueAnalyticsService.get_revenue_summary(db, scenario)
    trend = RevenueAnalyticsService.get_revenue_trend(db, scenario)
    by_segment = RevenueAnalyticsService.get_revenue_by_segment(db, scenario)
    by_plan = RevenueAnalyticsService.get_revenue_by_plan(db, scenario)

    rows: List[Dict[str, Any]] = []

    # Summary row
    if isinstance(summary, dict):
        row = {"section": "summary", "scenario": scenario}
        row.update(_flatten_dict(summary))
        rows.append(row)

    # Trend rows
    if isinstance(trend, list):
        for item in trend:
            if isinstance(item, dict):
                row = {"section": "trend", "scenario": scenario}
                row.update(item)
                rows.append(row)

    # By-segment rows
    if isinstance(by_segment, list):
        for item in by_segment:
            if isinstance(item, dict):
                row = {"section": "by_segment", "scenario": scenario}
                row.update(item)
                rows.append(row)

    # By-plan rows
    if isinstance(by_plan, list):
        for item in by_plan:
            if isinstance(item, dict):
                row = {"section": "by_plan", "scenario": scenario}
                row.update(item)
                rows.append(row)

    return _dict_list_to_csv(rows)


def _build_transactions_report(db: Session, scenario: str) -> str:
    """Build a CSV of transaction data."""
    result = TransactionAnalyticsService.get_transactions_paginated(
        db, scenario=scenario, skip=0, limit=10000,
        status=None, payment_method=None,
        start_date=None, end_date=None,
    )

    if isinstance(result, dict) and "items" in result:
        rows = result["items"]
    elif isinstance(result, list):
        rows = result
    else:
        rows = [result] if isinstance(result, dict) else []

    processed_rows: List[Dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            processed_rows.append(row)
        elif hasattr(row, "__dict__"):
            d = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
            processed_rows.append(d)

    return _dict_list_to_csv(processed_rows)


def _build_products_report(db: Session, scenario: str) -> str:
    """Build a CSV of product usage data."""
    summary = ProductAnalyticsService.get_product_summary(db, scenario)
    features = ProductAnalyticsService.get_feature_adoption(db, scenario)
    trend = ProductAnalyticsService.get_usage_trend(db, scenario)

    rows: List[Dict[str, Any]] = []

    # Summary
    if isinstance(summary, dict):
        row = {"section": "summary", "scenario": scenario}
        row.update(_flatten_dict(summary))
        rows.append(row)

    # Feature rows
    if isinstance(features, list):
        for item in features:
            if isinstance(item, dict):
                row = {"section": "features", "scenario": scenario}
                row.update(item)
                rows.append(row)

    # Trend rows
    if isinstance(trend, list):
        for item in trend:
            if isinstance(item, dict):
                row = {"section": "trend", "scenario": scenario}
                row.update(item)
                rows.append(row)

    return _dict_list_to_csv(rows)


# Mapping of report_type -> builder function
_REPORT_BUILDERS = {
    "business_performance": _build_business_performance_report,
    "customer_analytics": _build_customer_analytics_report,
    "revenue": _build_revenue_report,
    "transactions": _build_transactions_report,
    "products": _build_products_report,
}


@router.get("/export")
def export_report(
    scenario: str = Query("fintech", description="Business scenario"),
    report_type: str = Query(
        ...,
        description="Report type: business_performance, customer_analytics, revenue, transactions, products",
    ),
    format: str = Query("csv", description="Export format (only csv supported)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export a report as a downloadable CSV file.

    Supported report types:
    - business_performance: Combined KPI and revenue trend
    - customer_analytics: Full customer list
    - revenue: Revenue summary, trend, and breakdowns
    - transactions: Transaction list
    - products: Product usage and feature adoption
    """
    if format.lower() != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV export format is currently supported",
        )

    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report type '{report_type}'. Valid types: {', '.join(sorted(VALID_REPORT_TYPES))}",
        )

    builder = _REPORT_BUILDERS[report_type]
    csv_content = builder(db, scenario)

    if not csv_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data available for the requested report",
        )

    filename = f"{report_type}_{scenario}.csv"

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )
