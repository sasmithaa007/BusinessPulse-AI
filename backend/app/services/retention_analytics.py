from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
from datetime import date, timedelta
from app.models import Customer


class RetentionAnalyticsService:

    @staticmethod
    def get_retention_stats(db: Session, scenario: str) -> dict:
        active = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.status == "active",
            )
            .scalar()
        )

        inactive = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.status == "inactive",
            )
            .scalar()
        )

        churned = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.status == "churned",
            )
            .scalar()
        )

        total = active + inactive + churned
        retention_rate = round((active / (active + inactive)) * 100, 2) if (active + inactive) > 0 else 0.0
        overall_retention = round((active / total) * 100, 2) if total > 0 else 0.0

        return {
            "active_customers": active,
            "inactive_customers": inactive,
            "churned_customers": churned,
            "total_customers": total,
            "retention_rate": retention_rate,
            "overall_retention_rate": overall_retention,
        }

    @staticmethod
    def get_monthly_retention(db: Session, scenario: str) -> list:
        twelve_months_ago = date.today() - timedelta(days=365)

        results = (
            db.query(
                extract("year", Customer.signup_date).label("year"),
                extract("month", Customer.signup_date).label("month"),
                func.count(Customer.id).label("total"),
                func.sum(
                    case((Customer.status == "active", 1), else_=0)
                ).label("active"),
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

        monthly = []
        for row in results:
            total = row.total or 0
            active = row.active or 0
            retention = round((active / total) * 100, 2) if total > 0 else 0.0
            monthly.append(
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "period": f"{int(row.year)}-{int(row.month):02d}",
                    "total_cohort": total,
                    "retained": active,
                    "retention_rate": retention,
                }
            )

        return monthly

    @staticmethod
    def get_cohort_retention(db: Session, scenario: str) -> list:
        twelve_months_ago = date.today() - timedelta(days=365)

        cohort_data = (
            db.query(
                extract("year", Customer.signup_date).label("year"),
                extract("month", Customer.signup_date).label("month"),
                Customer.id,
                Customer.status,
                Customer.signup_date,
            )
            .filter(
                Customer.business_scenario == scenario,
                Customer.signup_date >= twelve_months_ago,
            )
            .all()
        )

        cohorts = {}
        for row in cohort_data:
            cohort_key = f"{int(row.year)}-{int(row.month):02d}"
            if cohort_key not in cohorts:
                cohorts[cohort_key] = {"total": 0, "active": 0, "signup_dates": []}
            cohorts[cohort_key]["total"] += 1
            if row.status == "active":
                cohorts[cohort_key]["active"] += 1
            if row.signup_date:
                cohorts[cohort_key]["signup_dates"].append(row.signup_date)

        result = []
        today = date.today()
        for cohort_key in sorted(cohorts.keys()):
            data = cohorts[cohort_key]
            total = data["total"]
            active = data["active"]

            parts = cohort_key.split("-")
            cohort_year = int(parts[0])
            cohort_month = int(parts[1])
            cohort_start = date(cohort_year, cohort_month, 1)
            months_elapsed = (today.year - cohort_start.year) * 12 + (today.month - cohort_start.month)

            retention_1m = round((active / total) * 100, 2) if total > 0 and months_elapsed >= 1 else None
            retention_3m = round((active / total) * 100, 2) if total > 0 and months_elapsed >= 3 else None
            retention_6m = round((active / total) * 100, 2) if total > 0 and months_elapsed >= 6 else None

            result.append(
                {
                    "cohort": cohort_key,
                    "cohort_size": total,
                    "current_active": active,
                    "retention_1_month": retention_1m,
                    "retention_3_months": retention_3m,
                    "retention_6_months": retention_6m,
                }
            )

        return result

    @staticmethod
    def get_retention_by_segment(db: Session, scenario: str) -> list:
        results = (
            db.query(
                Customer.segment,
                func.count(Customer.id).label("total"),
                func.sum(
                    case((Customer.status == "active", 1), else_=0)
                ).label("active"),
                func.sum(
                    case((Customer.status == "inactive", 1), else_=0)
                ).label("inactive"),
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
            total = row.total or 0
            active = row.active or 0
            inactive = row.inactive or 0
            base = active + inactive
            retention = round((active / base) * 100, 2) if base > 0 else 0.0
            segments.append(
                {
                    "segment": row.segment or "Unknown",
                    "total": total,
                    "active": active,
                    "inactive": inactive,
                    "churned": row.churned or 0,
                    "retention_rate": retention,
                }
            )

        return segments
