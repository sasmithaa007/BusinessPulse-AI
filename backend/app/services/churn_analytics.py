from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
from datetime import date, timedelta
from app.models import Customer


class ChurnAnalyticsService:

    @staticmethod
    def get_churn_stats(
        db: Session,
        scenario: str,
        start_date: date = None,
        end_date: date = None,
    ) -> dict:
        query = db.query(Customer).filter(Customer.business_scenario == scenario)

        if start_date:
            query = query.filter(Customer.signup_date >= start_date)
        if end_date:
            query = query.filter(Customer.signup_date <= end_date)

        total_active = query.filter(Customer.status == "active").count()
        total_inactive = query.filter(Customer.status == "inactive").count()
        total_churned = query.filter(Customer.status == "churned").count()

        denominator = total_active + total_inactive + total_churned
        churn_rate = round((total_churned / denominator) * 100, 2) if denominator > 0 else 0.0

        at_risk = query.filter(
            Customer.churn_risk_score > 66,
            Customer.status != "churned",
        ).count()

        avg_risk_score = (
            db.query(func.coalesce(func.avg(Customer.churn_risk_score), 0))
            .filter(Customer.business_scenario == scenario)
            .scalar()
        )

        return {
            "churn_rate": churn_rate,
            "total_churned": total_churned,
            "total_active": total_active,
            "total_inactive": total_inactive,
            "at_risk_customers": at_risk,
            "avg_risk_score": round(float(avg_risk_score), 2),
        }

    @staticmethod
    def get_churn_by_segment(db: Session, scenario: str) -> list:
        results = (
            db.query(
                Customer.segment,
                func.count(Customer.id).label("total"),
                func.sum(
                    case((Customer.status == "churned", 1), else_=0)
                ).label("churned"),
            )
            .filter(Customer.business_scenario == scenario)
            .group_by(Customer.segment)
            .all()
        )

        segments = []
        for row in results:
            segment_name = row.segment or "Unknown"
            total = row.total or 0
            churned = row.churned or 0
            churn_rate = round((churned / total) * 100, 2) if total > 0 else 0.0
            segments.append(
                {
                    "segment": segment_name,
                    "total": total,
                    "churned": churned,
                    "churn_rate": churn_rate,
                }
            )

        return segments

    @staticmethod
    def get_churn_trend(db: Session, scenario: str) -> list:
        twelve_months_ago = date.today() - timedelta(days=365)

        results = (
            db.query(
                extract("year", Customer.signup_date).label("year"),
                extract("month", Customer.signup_date).label("month"),
                func.count(Customer.id).label("total"),
                func.sum(
                    case((Customer.status == "churned", 1), else_=0)
                ).label("churned"),
            )
            .filter(
                Customer.business_scenario == scenario,
                Customer.signup_date >= twelve_months_ago,
            )
            .group_by(
                extract("year", Customer.signup_date),
                extract("month", Customer.signup_date),
            )
            .order_by(
                extract("year", Customer.signup_date),
                extract("month", Customer.signup_date),
            )
            .all()
        )

        trend = []
        for row in results:
            total = row.total or 0
            churned = row.churned or 0
            churn_rate = round((churned / total) * 100, 2) if total > 0 else 0.0
            trend.append(
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "period": f"{int(row.year)}-{int(row.month):02d}",
                    "total_cohort": total,
                    "churned": churned,
                    "churn_rate": churn_rate,
                }
            )

        return trend

    @staticmethod
    def get_churn_risk_distribution(db: Session, scenario: str) -> dict:
        low = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.churn_risk_score >= 0,
                Customer.churn_risk_score <= 33,
            )
            .scalar()
        )

        medium = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.churn_risk_score >= 34,
                Customer.churn_risk_score <= 66,
            )
            .scalar()
        )

        high = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.churn_risk_score >= 67,
                Customer.churn_risk_score <= 100,
            )
            .scalar()
        )

        total = low + medium + high

        return {
            "low": {
                "label": "Low Risk (0-33)",
                "count": low,
                "percentage": round((low / total) * 100, 2) if total > 0 else 0.0,
            },
            "medium": {
                "label": "Medium Risk (34-66)",
                "count": medium,
                "percentage": round((medium / total) * 100, 2) if total > 0 else 0.0,
            },
            "high": {
                "label": "High Risk (67-100)",
                "count": high,
                "percentage": round((high / total) * 100, 2) if total > 0 else 0.0,
            },
            "total": total,
        }
