import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
from datetime import date, timedelta
from app.models import ApiLog


class PerformanceAnalyticsService:

    @staticmethod
    def get_performance_summary(db: Session, scenario: str) -> dict:
        total_requests = (
            db.query(func.count(ApiLog.id))
            .filter(ApiLog.business_scenario == scenario)
            .scalar()
        )

        avg_response = (
            db.query(func.coalesce(func.avg(ApiLog.response_time_ms), 0))
            .filter(ApiLog.business_scenario == scenario)
            .scalar()
        )

        response_times = (
            db.query(ApiLog.response_time_ms)
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.response_time_ms.isnot(None),
            )
            .all()
        )

        times_array = [float(r.response_time_ms) for r in response_times if r.response_time_ms is not None]

        if times_array:
            arr = np.array(times_array)
            median_response = float(np.median(arr))
            p95_response = float(np.percentile(arr, 95))
            p99_response = float(np.percentile(arr, 99))
        else:
            median_response = 0.0
            p95_response = 0.0
            p99_response = 0.0

        error_count = (
            db.query(func.count(ApiLog.id))
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 400,
            )
            .scalar()
        )

        error_rate = round((error_count / total_requests) * 100, 2) if total_requests > 0 else 0.0

        success_count = (
            db.query(func.count(ApiLog.id))
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 200,
                ApiLog.status_code < 300,
            )
            .scalar()
        )

        return {
            "total_requests": total_requests or 0,
            "avg_response_time_ms": round(float(avg_response), 2),
            "median_response_time_ms": round(median_response, 2),
            "p95_response_time_ms": round(p95_response, 2),
            "p99_response_time_ms": round(p99_response, 2),
            "error_rate": error_rate,
            "error_count": error_count or 0,
            "success_count": success_count or 0,
        }

    @staticmethod
    def get_endpoint_performance(db: Session, scenario: str) -> list:
        results = (
            db.query(
                ApiLog.endpoint,
                ApiLog.method,
                func.count(ApiLog.id).label("request_count"),
                func.coalesce(func.avg(ApiLog.response_time_ms), 0).label("avg_time"),
                func.coalesce(func.min(ApiLog.response_time_ms), 0).label("min_time"),
                func.coalesce(func.max(ApiLog.response_time_ms), 0).label("max_time"),
                func.sum(
                    case((ApiLog.status_code >= 400, 1), else_=0)
                ).label("error_count"),
            )
            .filter(ApiLog.business_scenario == scenario)
            .group_by(ApiLog.endpoint, ApiLog.method)
            .order_by(func.count(ApiLog.id).desc())
            .all()
        )

        endpoints = []
        for row in results:
            req_count = row.request_count or 0
            errors = row.error_count or 0
            error_rate = round((errors / req_count) * 100, 2) if req_count > 0 else 0.0
            endpoints.append(
                {
                    "endpoint": row.endpoint,
                    "method": row.method,
                    "request_count": req_count,
                    "avg_response_time_ms": round(float(row.avg_time), 2),
                    "min_response_time_ms": round(float(row.min_time), 2),
                    "max_response_time_ms": round(float(row.max_time), 2),
                    "error_count": errors,
                    "error_rate": error_rate,
                }
            )

        return endpoints

    @staticmethod
    def get_slow_endpoints(db: Session, scenario: str, threshold_ms: float = 500) -> list:
        results = (
            db.query(
                ApiLog.endpoint,
                ApiLog.method,
                func.count(ApiLog.id).label("request_count"),
                func.coalesce(func.avg(ApiLog.response_time_ms), 0).label("avg_time"),
                func.coalesce(func.max(ApiLog.response_time_ms), 0).label("max_time"),
            )
            .filter(ApiLog.business_scenario == scenario)
            .group_by(ApiLog.endpoint, ApiLog.method)
            .having(func.avg(ApiLog.response_time_ms) > threshold_ms)
            .order_by(func.avg(ApiLog.response_time_ms).desc())
            .all()
        )

        slow = []
        for row in results:
            slow.append(
                {
                    "endpoint": row.endpoint,
                    "method": row.method,
                    "request_count": row.request_count,
                    "avg_response_time_ms": round(float(row.avg_time), 2),
                    "max_response_time_ms": round(float(row.max_time), 2),
                    "threshold_ms": threshold_ms,
                }
            )

        return slow

    @staticmethod
    def get_error_distribution(db: Session, scenario: str) -> dict:
        two_xx = (
            db.query(func.count(ApiLog.id))
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 200,
                ApiLog.status_code < 300,
            )
            .scalar()
        )

        three_xx = (
            db.query(func.count(ApiLog.id))
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 300,
                ApiLog.status_code < 400,
            )
            .scalar()
        )

        four_xx = (
            db.query(func.count(ApiLog.id))
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 400,
                ApiLog.status_code < 500,
            )
            .scalar()
        )

        five_xx = (
            db.query(func.count(ApiLog.id))
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 500,
            )
            .scalar()
        )

        total = (two_xx or 0) + (three_xx or 0) + (four_xx or 0) + (five_xx or 0)

        by_error_type = (
            db.query(
                ApiLog.error_type,
                func.count(ApiLog.id).label("count"),
            )
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 400,
                ApiLog.error_type.isnot(None),
            )
            .group_by(ApiLog.error_type)
            .order_by(func.count(ApiLog.id).desc())
            .all()
        )

        error_types = [
            {"error_type": row.error_type, "count": row.count}
            for row in by_error_type
        ]

        return {
            "2xx": {"label": "Success (2xx)", "count": two_xx or 0, "percentage": round(((two_xx or 0) / total) * 100, 2) if total > 0 else 0.0},
            "3xx": {"label": "Redirect (3xx)", "count": three_xx or 0, "percentage": round(((three_xx or 0) / total) * 100, 2) if total > 0 else 0.0},
            "4xx": {"label": "Client Error (4xx)", "count": four_xx or 0, "percentage": round(((four_xx or 0) / total) * 100, 2) if total > 0 else 0.0},
            "5xx": {"label": "Server Error (5xx)", "count": five_xx or 0, "percentage": round(((five_xx or 0) / total) * 100, 2) if total > 0 else 0.0},
            "total": total,
            "by_error_type": error_types,
        }
