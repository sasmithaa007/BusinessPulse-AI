from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract, desc
from datetime import date, timedelta
from app.models import OperationalRecord


class OperationalAnalyticsService:

    @staticmethod
    def get_operations_summary(db: Session, scenario: str) -> dict:
        base = db.query(OperationalRecord).filter(
            OperationalRecord.business_scenario == scenario
        )

        total = base.count()
        success = base.filter(OperationalRecord.process_status == "success").count()
        failed = base.filter(OperationalRecord.process_status == "failed").count()

        avg_time = (
            db.query(func.coalesce(func.avg(OperationalRecord.processing_time_seconds), 0))
            .filter(OperationalRecord.business_scenario == scenario)
            .scalar()
        )

        total_cost = (
            db.query(func.coalesce(func.sum(OperationalRecord.operational_cost), 0))
            .filter(OperationalRecord.business_scenario == scenario)
            .scalar()
        )

        success_rate = round((success / total) * 100, 2) if total > 0 else 0.0
        failure_rate = round((failed / total) * 100, 2) if total > 0 else 0.0

        avg_cost = (
            db.query(func.coalesce(func.avg(OperationalRecord.operational_cost), 0))
            .filter(OperationalRecord.business_scenario == scenario)
            .scalar()
        )

        return {
            "total_operations": total,
            "successful": success,
            "failed": failed,
            "avg_processing_time_seconds": round(float(avg_time), 2),
            "total_operational_cost": round(float(total_cost), 2),
            "avg_operational_cost": round(float(avg_cost), 2),
            "success_rate": success_rate,
            "failure_rate": failure_rate,
        }

    @staticmethod
    def get_bottlenecks(db: Session, scenario: str) -> list:
        results = (
            db.query(
                OperationalRecord.process_name,
                func.coalesce(func.avg(OperationalRecord.processing_time_seconds), 0).label("avg_time"),
                func.coalesce(func.max(OperationalRecord.processing_time_seconds), 0).label("max_time"),
                func.count(OperationalRecord.id).label("execution_count"),
                func.sum(
                    case(
                        (OperationalRecord.process_status == "failed", 1),
                        else_=0,
                    )
                ).label("failure_count"),
            )
            .filter(OperationalRecord.business_scenario == scenario)
            .group_by(OperationalRecord.process_name)
            .order_by(func.avg(OperationalRecord.processing_time_seconds).desc())
            .limit(10)
            .all()
        )

        bottlenecks = []
        for row in results:
            exec_count = row.execution_count or 0
            failures = row.failure_count or 0
            failure_rate = round((failures / exec_count) * 100, 2) if exec_count > 0 else 0.0
            bottlenecks.append(
                {
                    "process_name": row.process_name,
                    "avg_processing_time_seconds": round(float(row.avg_time), 2),
                    "max_processing_time_seconds": round(float(row.max_time), 2),
                    "execution_count": exec_count,
                    "failure_count": failures,
                    "failure_rate": failure_rate,
                }
            )

        return bottlenecks

    @staticmethod
    def get_cost_trend(db: Session, scenario: str) -> list:
        twelve_months_ago = date.today() - timedelta(days=365)

        results = (
            db.query(
                extract("year", OperationalRecord.recorded_date).label("year"),
                extract("month", OperationalRecord.recorded_date).label("month"),
                func.coalesce(func.sum(OperationalRecord.operational_cost), 0).label("total_cost"),
                func.count(OperationalRecord.id).label("operation_count"),
                func.coalesce(func.avg(OperationalRecord.operational_cost), 0).label("avg_cost"),
            )
            .filter(
                OperationalRecord.business_scenario == scenario,
                OperationalRecord.recorded_date >= twelve_months_ago,
            )
            .group_by(
                extract("year", OperationalRecord.recorded_date),
                extract("month", OperationalRecord.recorded_date),
            )
            .order_by(
                extract("year", OperationalRecord.recorded_date),
                extract("month", OperationalRecord.recorded_date),
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
                    "total_cost": round(float(row.total_cost), 2),
                    "operation_count": row.operation_count,
                    "avg_cost": round(float(row.avg_cost), 2),
                }
            )

        return trend

    @staticmethod
    def get_process_breakdown(db: Session, scenario: str) -> list:
        results = (
            db.query(
                OperationalRecord.process_name,
                OperationalRecord.department,
                func.count(OperationalRecord.id).label("count"),
                func.coalesce(func.avg(OperationalRecord.processing_time_seconds), 0).label("avg_time"),
                func.coalesce(func.avg(OperationalRecord.operational_cost), 0).label("avg_cost"),
                func.coalesce(func.sum(OperationalRecord.operational_cost), 0).label("total_cost"),
                func.sum(
                    case(
                        (OperationalRecord.process_status == "failed", 1),
                        else_=0,
                    )
                ).label("failure_count"),
            )
            .filter(OperationalRecord.business_scenario == scenario)
            .group_by(OperationalRecord.process_name, OperationalRecord.department)
            .order_by(func.count(OperationalRecord.id).desc())
            .all()
        )

        processes = []
        for row in results:
            count = row.count or 0
            failures = row.failure_count or 0
            failure_rate = round((failures / count) * 100, 2) if count > 0 else 0.0
            processes.append(
                {
                    "process_name": row.process_name,
                    "department": row.department or "Unknown",
                    "execution_count": count,
                    "avg_processing_time_seconds": round(float(row.avg_time), 2),
                    "avg_cost": round(float(row.avg_cost), 2),
                    "total_cost": round(float(row.total_cost), 2),
                    "failure_count": failures,
                    "failure_rate": failure_rate,
                }
            )

        return processes
