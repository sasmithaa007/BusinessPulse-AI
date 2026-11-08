from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract, desc
from datetime import date, timedelta
from app.models import Customer, Transaction


class TransactionAnalyticsService:

    @staticmethod
    def get_transaction_summary(db: Session, scenario: str) -> dict:
        base = db.query(Transaction).filter(Transaction.business_scenario == scenario)

        total = base.count()
        success = base.filter(Transaction.status == "successful").count()
        failed = base.filter(Transaction.status == "failed").count()
        pending = base.filter(Transaction.status == "pending").count()

        success_rate = round((success / total) * 100, 2) if total > 0 else 0.0
        failure_rate = round((failed / total) * 100, 2) if total > 0 else 0.0

        avg_value = (
            db.query(func.coalesce(func.avg(Transaction.amount), 0))
            .filter(Transaction.business_scenario == scenario)
            .scalar()
        )

        avg_processing_time = (
            db.query(func.coalesce(func.avg(Transaction.processing_time_ms), 0))
            .filter(Transaction.business_scenario == scenario)
            .scalar()
        )

        total_volume = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
            )
            .scalar()
        )

        return {
            "total_transactions": total,
            "successful": success,
            "failed": failed,
            "pending": pending,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "avg_transaction_value": round(float(avg_value), 2),
            "avg_processing_time_ms": round(float(avg_processing_time), 2),
            "total_volume": round(float(total_volume), 2),
        }

    @staticmethod
    def get_transactions_paginated(
        db: Session,
        scenario: str,
        skip: int = 0,
        limit: int = 20,
        status: str = None,
        payment_method: str = None,
        start_date: date = None,
        end_date: date = None,
    ) -> dict:
        query = (
            db.query(
                Transaction.id,
                Transaction.transaction_code,
                Transaction.transaction_date,
                Transaction.amount,
                Transaction.currency,
                Transaction.status,
                Transaction.payment_method,
                Transaction.failure_reason,
                Transaction.gateway,
                Transaction.processing_time_ms,
                Customer.name.label("customer_name"),
                Customer.customer_code.label("customer_code"),
            )
            .outerjoin(Customer, Transaction.customer_id == Customer.id)
            .filter(Transaction.business_scenario == scenario)
        )

        if status:
            query = query.filter(Transaction.status == status)
        if payment_method:
            query = query.filter(Transaction.payment_method == payment_method)
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        total = query.count()
        rows = (
            query.order_by(desc(Transaction.transaction_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

        items = []
        for r in rows:
            items.append(
                {
                    "id": r.id,
                    "transaction_code": r.transaction_code,
                    "transaction_date": str(r.transaction_date) if r.transaction_date else None,
                    "amount": round(float(r.amount), 2) if r.amount else 0.0,
                    "currency": r.currency,
                    "status": r.status,
                    "payment_method": r.payment_method,
                    "failure_reason": r.failure_reason,
                    "gateway": r.gateway,
                    "processing_time_ms": float(r.processing_time_ms) if r.processing_time_ms else 0.0,
                    "customer_name": r.customer_name,
                    "customer_code": r.customer_code,
                }
            )

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
        }

    @staticmethod
    def get_failure_analysis(db: Session, scenario: str) -> dict:
        by_reason = (
            db.query(
                Transaction.failure_reason,
                func.count(Transaction.id).label("count"),
                func.coalesce(func.sum(Transaction.amount), 0).label("total_amount"),
            )
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "failed",
            )
            .group_by(Transaction.failure_reason)
            .order_by(func.count(Transaction.id).desc())
            .all()
        )

        by_method = (
            db.query(
                Transaction.payment_method,
                func.count(Transaction.id).label("total"),
                func.sum(
                    case((Transaction.status == "failed", 1), else_=0)
                ).label("failed"),
            )
            .filter(Transaction.business_scenario == scenario)
            .group_by(Transaction.payment_method)
            .all()
        )

        reasons = []
        for row in by_reason:
            reasons.append(
                {
                    "failure_reason": row.failure_reason or "Unknown",
                    "count": row.count,
                    "total_amount": round(float(row.total_amount), 2),
                }
            )

        method_failures = []
        for row in by_method:
            total = row.total or 0
            failed = row.failed or 0
            failure_rate = round((failed / total) * 100, 2) if total > 0 else 0.0
            method_failures.append(
                {
                    "payment_method": row.payment_method or "Unknown",
                    "total_transactions": total,
                    "failed_transactions": failed,
                    "failure_rate": failure_rate,
                }
            )

        by_gateway = (
            db.query(
                Transaction.gateway,
                func.count(Transaction.id).label("total"),
                func.sum(
                    case((Transaction.status == "failed", 1), else_=0)
                ).label("failed"),
            )
            .filter(Transaction.business_scenario == scenario)
            .group_by(Transaction.gateway)
            .all()
        )

        gateway_failures = []
        for row in by_gateway:
            total = row.total or 0
            failed = row.failed or 0
            failure_rate = round((failed / total) * 100, 2) if total > 0 else 0.0
            gateway_failures.append(
                {
                    "gateway": row.gateway or "Unknown",
                    "total_transactions": total,
                    "failed_transactions": failed,
                    "failure_rate": failure_rate,
                }
            )

        return {
            "by_failure_reason": reasons,
            "by_payment_method": method_failures,
            "by_gateway": gateway_failures,
        }

    @staticmethod
    def get_transaction_trend(db: Session, scenario: str) -> list:
        twelve_months_ago = date.today() - timedelta(days=365)

        results = (
            db.query(
                extract("year", Transaction.transaction_date).label("year"),
                extract("month", Transaction.transaction_date).label("month"),
                func.sum(
                    case((Transaction.status == "successful", 1), else_=0)
                ).label("success_count"),
                func.sum(
                    case((Transaction.status == "failed", 1), else_=0)
                ).label("failed_count"),
                func.count(Transaction.id).label("total_count"),
                func.coalesce(func.sum(Transaction.amount), 0).label("total_amount"),
            )
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.transaction_date >= twelve_months_ago,
            )
            .group_by(
                extract("year", Transaction.transaction_date),
                extract("month", Transaction.transaction_date),
            )
            .order_by(
                extract("year", Transaction.transaction_date),
                extract("month", Transaction.transaction_date),
            )
            .all()
        )

        trend = []
        for row in results:
            trend.append(
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "period": f"{int(row.year)}-{int(row.month):02d}",
                    "success_count": row.success_count or 0,
                    "failed_count": row.failed_count or 0,
                    "total_count": row.total_count or 0,
                    "total_amount": round(float(row.total_amount), 2),
                }
            )

        return trend
