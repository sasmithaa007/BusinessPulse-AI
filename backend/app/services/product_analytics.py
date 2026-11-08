from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract, desc
from datetime import date, timedelta
from app.models import Customer, ProductUsage


class ProductAnalyticsService:

    @staticmethod
    def get_product_summary(db: Session, scenario: str) -> dict:
        active_users = (
            db.query(func.count(func.distinct(ProductUsage.customer_id)))
            .filter(ProductUsage.business_scenario == scenario)
            .scalar()
        )

        total_events = (
            db.query(func.coalesce(func.sum(ProductUsage.usage_count), 0))
            .filter(ProductUsage.business_scenario == scenario)
            .scalar()
        )

        avg_session = (
            db.query(func.coalesce(func.avg(ProductUsage.session_duration_minutes), 0))
            .filter(ProductUsage.business_scenario == scenario)
            .scalar()
        )

        top_features_rows = (
            db.query(
                ProductUsage.feature_name,
                func.coalesce(func.sum(ProductUsage.usage_count), 0).label("total_usage"),
            )
            .filter(ProductUsage.business_scenario == scenario)
            .group_by(ProductUsage.feature_name)
            .order_by(func.sum(ProductUsage.usage_count).desc())
            .limit(5)
            .all()
        )

        top_features = [
            {"feature": row.feature_name, "usage_count": int(row.total_usage)}
            for row in top_features_rows
        ]

        total_records = (
            db.query(func.count(ProductUsage.id))
            .filter(ProductUsage.business_scenario == scenario)
            .scalar()
        )

        return {
            "active_users": active_users or 0,
            "total_events": int(total_events),
            "total_records": total_records or 0,
            "avg_session_duration_minutes": round(float(avg_session), 2),
            "top_features": top_features,
        }

    @staticmethod
    def get_feature_adoption(db: Session, scenario: str) -> list:
        total_customers = (
            db.query(func.count(Customer.id))
            .filter(Customer.business_scenario == scenario)
            .scalar()
        )

        features = (
            db.query(
                ProductUsage.feature_name,
                func.count(func.distinct(ProductUsage.customer_id)).label("unique_users"),
                func.coalesce(func.sum(ProductUsage.usage_count), 0).label("total_usage"),
                func.coalesce(func.avg(ProductUsage.session_duration_minutes), 0).label("avg_session"),
            )
            .filter(ProductUsage.business_scenario == scenario)
            .group_by(ProductUsage.feature_name)
            .order_by(func.count(func.distinct(ProductUsage.customer_id)).desc())
            .all()
        )

        result = []
        for row in features:
            unique = row.unique_users or 0
            adoption = round((unique / total_customers) * 100, 2) if total_customers > 0 else 0.0
            result.append(
                {
                    "feature_name": row.feature_name,
                    "unique_users": unique,
                    "total_usage": int(row.total_usage),
                    "avg_session_duration": round(float(row.avg_session), 2),
                    "adoption_rate": adoption,
                }
            )

        return result

    @staticmethod
    def get_usage_trend(db: Session, scenario: str) -> list:
        twelve_months_ago = date.today() - timedelta(days=365)

        results = (
            db.query(
                extract("year", ProductUsage.usage_date).label("year"),
                extract("month", ProductUsage.usage_date).label("month"),
                func.coalesce(func.sum(ProductUsage.usage_count), 0).label("total_usage"),
                func.count(func.distinct(ProductUsage.customer_id)).label("active_users"),
                func.coalesce(func.avg(ProductUsage.session_duration_minutes), 0).label("avg_session"),
            )
            .filter(
                ProductUsage.business_scenario == scenario,
                ProductUsage.usage_date >= twelve_months_ago,
            )
            .group_by(
                extract("year", ProductUsage.usage_date),
                extract("month", ProductUsage.usage_date),
            )
            .order_by(
                extract("year", ProductUsage.usage_date),
                extract("month", ProductUsage.usage_date),
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
                    "total_usage": int(row.total_usage),
                    "active_users": row.active_users or 0,
                    "avg_session_duration": round(float(row.avg_session), 2),
                }
            )

        return trend

    @staticmethod
    def get_usage_by_segment(db: Session, scenario: str) -> list:
        results = (
            db.query(
                Customer.segment,
                func.coalesce(func.sum(ProductUsage.usage_count), 0).label("total_usage"),
                func.count(func.distinct(ProductUsage.customer_id)).label("active_users"),
                func.coalesce(func.avg(ProductUsage.session_duration_minutes), 0).label("avg_session"),
            )
            .join(Customer, ProductUsage.customer_id == Customer.id)
            .filter(ProductUsage.business_scenario == scenario)
            .group_by(Customer.segment)
            .all()
        )

        segments = []
        for row in results:
            active = row.active_users or 0
            total_usage = int(row.total_usage)
            avg_per_user = round(total_usage / active, 2) if active > 0 else 0.0
            segments.append(
                {
                    "segment": row.segment or "Unknown",
                    "total_usage": total_usage,
                    "active_users": active,
                    "avg_usage_per_user": avg_per_user,
                    "avg_session_duration": round(float(row.avg_session), 2),
                }
            )

        return segments
