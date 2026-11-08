from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
from datetime import date, timedelta
from app.models import Customer, Transaction, Subscription


class RevenueAnalyticsService:

    @staticmethod
    def get_revenue_summary(db: Session, scenario: str) -> dict:
        total_revenue = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
            )
            .scalar()
        )

        today = date.today()
        current_month_start = today.replace(day=1)
        prev_month_end = current_month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        current_month_revenue = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
                Transaction.transaction_date >= current_month_start,
            )
            .scalar()
        )

        prev_month_revenue = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
                Transaction.transaction_date >= prev_month_start,
                Transaction.transaction_date <= prev_month_end,
            )
            .scalar()
        )

        mrr = (
            db.query(func.coalesce(func.sum(Subscription.monthly_amount), 0))
            .filter(
                Subscription.business_scenario == scenario,
                Subscription.subscription_status == "active",
            )
            .scalar()
        )

        failed_billing = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "failed",
            )
            .scalar()
        )

        revenue_growth = 0.0
        prev = float(prev_month_revenue)
        curr = float(current_month_revenue)
        if prev > 0:
            revenue_growth = round(((curr - prev) / prev) * 100, 2)

        estimated_recoverable = round(float(failed_billing) * 0.5, 2)

        return {
            "total_revenue": round(float(total_revenue), 2),
            "current_month_revenue": round(curr, 2),
            "previous_month_revenue": round(prev, 2),
            "mrr": round(float(mrr), 2),
            "failed_billing": round(float(failed_billing), 2),
            "revenue_growth_pct": revenue_growth,
            "estimated_recoverable": estimated_recoverable,
        }

    @staticmethod
    def get_revenue_trend(db: Session, scenario: str) -> list:
        twelve_months_ago = date.today() - timedelta(days=365)

        results = (
            db.query(
                extract("year", Transaction.transaction_date).label("year"),
                extract("month", Transaction.transaction_date).label("month"),
                func.coalesce(func.sum(Transaction.amount), 0).label("revenue"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
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
                    "revenue": round(float(row.revenue), 2),
                    "transaction_count": row.transaction_count,
                }
            )

        return trend

    @staticmethod
    def get_revenue_by_segment(db: Session, scenario: str) -> list:
        results = (
            db.query(
                Customer.segment,
                func.coalesce(func.sum(Transaction.amount), 0).label("revenue"),
                func.count(func.distinct(Customer.id)).label("customer_count"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .join(Transaction, Transaction.customer_id == Customer.id)
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
            )
            .group_by(Customer.segment)
            .all()
        )

        segments = []
        for row in results:
            customer_count = row.customer_count or 0
            revenue = float(row.revenue)
            avg_revenue = round(revenue / customer_count, 2) if customer_count > 0 else 0.0
            segments.append(
                {
                    "segment": row.segment or "Unknown",
                    "revenue": round(revenue, 2),
                    "customer_count": customer_count,
                    "transaction_count": row.transaction_count,
                    "avg_revenue_per_customer": avg_revenue,
                }
            )

        return segments

    @staticmethod
    def get_revenue_leakage(db: Session, scenario: str) -> dict:
        total_failed = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "failed",
            )
            .scalar()
        )

        failed_count = (
            db.query(func.count(Transaction.id))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "failed",
            )
            .scalar()
        )

        by_payment_method = (
            db.query(
                Transaction.payment_method,
                func.coalesce(func.sum(Transaction.amount), 0).label("failed_amount"),
                func.count(Transaction.id).label("failed_count"),
            )
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "failed",
            )
            .group_by(Transaction.payment_method)
            .all()
        )

        by_reason = (
            db.query(
                Transaction.failure_reason,
                func.count(Transaction.id).label("count"),
                func.coalesce(func.sum(Transaction.amount), 0).label("amount"),
            )
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "failed",
                Transaction.failure_reason.isnot(None),
            )
            .group_by(Transaction.failure_reason)
            .order_by(func.count(Transaction.id).desc())
            .all()
        )

        method_breakdown = []
        for row in by_payment_method:
            method_breakdown.append(
                {
                    "payment_method": row.payment_method or "Unknown",
                    "failed_amount": round(float(row.failed_amount), 2),
                    "failed_count": row.failed_count,
                }
            )

        reason_breakdown = []
        for row in by_reason:
            reason_breakdown.append(
                {
                    "failure_reason": row.failure_reason or "Unknown",
                    "count": row.count,
                    "amount": round(float(row.amount), 2),
                }
            )

        total_failed_val = float(total_failed)
        return {
            "total_failed_amount": round(total_failed_val, 2),
            "total_failed_count": failed_count,
            "recovery_estimate": round(total_failed_val * 0.5, 2),
            "by_payment_method": method_breakdown,
            "by_failure_reason": reason_breakdown,
        }

    @staticmethod
    def get_revenue_by_plan(db: Session, scenario: str) -> list:
        results = (
            db.query(
                Subscription.plan_name,
                func.count(Subscription.id).label("subscriber_count"),
                func.coalesce(func.sum(Subscription.monthly_amount), 0).label("total_mrr"),
                func.coalesce(func.sum(Subscription.annual_amount), 0).label("total_arr"),
                func.coalesce(func.avg(Subscription.monthly_amount), 0).label("avg_monthly"),
            )
            .filter(
                Subscription.business_scenario == scenario,
                Subscription.subscription_status == "active",
            )
            .group_by(Subscription.plan_name)
            .all()
        )

        plans = []
        for row in results:
            plans.append(
                {
                    "plan_name": row.plan_name or "Unknown",
                    "subscriber_count": row.subscriber_count,
                    "total_mrr": round(float(row.total_mrr), 2),
                    "total_arr": round(float(row.total_arr), 2),
                    "avg_monthly_amount": round(float(row.avg_monthly), 2),
                }
            )

        return plans
