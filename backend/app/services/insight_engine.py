from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from app.models import Customer, Transaction, Subscription, ProductUsage, ApiLog, OperationalRecord


class InsightEngine:

    @staticmethod
    def get_insights(db: Session, scenario: str) -> list:
        insights = []
        insight_id = 0

        # --- CHURN INSIGHTS ---
        total_customers = (
            db.query(func.count(Customer.id))
            .filter(Customer.business_scenario == scenario)
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
        churn_rate = round((churned / total_customers) * 100, 2) if total_customers > 0 else 0.0

        if churn_rate > 20:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "High Customer Churn",
                    "metric": "churn_rate",
                    "observed_value": churn_rate,
                    "threshold": 20.0,
                    "explanation": f"Customer churn rate is {churn_rate}%, which exceeds the 20% critical threshold. "
                                   f"{churned} out of {total_customers} customers have churned.",
                    "recommended_action": "Implement targeted retention campaigns for at-risk customers. "
                                          "Analyze churn reasons by segment and deploy personalized re-engagement strategies.",
                    "priority": "high",
                    "evidence_level": "strong",
                }
            )
        elif churn_rate > 10:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "Elevated Customer Churn",
                    "metric": "churn_rate",
                    "observed_value": churn_rate,
                    "threshold": 10.0,
                    "explanation": f"Customer churn rate is {churn_rate}%, above the 10% warning threshold.",
                    "recommended_action": "Monitor churn trends closely and consider proactive outreach to inactive customers.",
                    "priority": "medium",
                    "evidence_level": "moderate",
                }
            )

        # --- AT-RISK CUSTOMERS ---
        at_risk = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.churn_risk_score > 66,
                Customer.status != "churned",
            )
            .scalar()
        )
        active_customers = (
            db.query(func.count(Customer.id))
            .filter(
                Customer.business_scenario == scenario,
                Customer.status == "active",
            )
            .scalar()
        )
        at_risk_pct = round((at_risk / active_customers) * 100, 2) if active_customers > 0 else 0.0

        if at_risk_pct > 25:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "Large At-Risk Customer Pool",
                    "metric": "at_risk_percentage",
                    "observed_value": at_risk_pct,
                    "threshold": 25.0,
                    "explanation": f"{at_risk} customers ({at_risk_pct}% of active) have high churn risk scores (>66). "
                                   "This indicates a significant portion of the customer base may churn soon.",
                    "recommended_action": "Prioritize intervention for high-risk customers with personalized retention offers, "
                                          "loyalty rewards, and dedicated account management.",
                    "priority": "high",
                    "evidence_level": "strong",
                }
            )

        # --- TRANSACTION FAILURE INSIGHTS ---
        total_txns = (
            db.query(func.count(Transaction.id))
            .filter(Transaction.business_scenario == scenario)
            .scalar()
        )
        failed_txns = (
            db.query(func.count(Transaction.id))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "failed",
            )
            .scalar()
        )
        failure_rate = round((failed_txns / total_txns) * 100, 2) if total_txns > 0 else 0.0

        if failure_rate > 15:
            insight_id += 1
            failed_amount = (
                db.query(func.coalesce(func.sum(Transaction.amount), 0))
                .filter(
                    Transaction.business_scenario == scenario,
                    Transaction.status == "failed",
                )
                .scalar()
            )
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "High Transaction Failure Rate",
                    "metric": "transaction_failure_rate",
                    "observed_value": failure_rate,
                    "threshold": 15.0,
                    "explanation": f"Transaction failure rate is {failure_rate}% ({failed_txns} failures). "
                                   f"Estimated revenue at risk: ${round(float(failed_amount), 2):,.2f}.",
                    "recommended_action": "Investigate top failure reasons. Review payment gateway configuration. "
                                          "Implement smart retry logic for transient failures.",
                    "priority": "high",
                    "evidence_level": "strong",
                }
            )
        elif failure_rate > 5:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "Elevated Transaction Failures",
                    "metric": "transaction_failure_rate",
                    "observed_value": failure_rate,
                    "threshold": 5.0,
                    "explanation": f"Transaction failure rate is {failure_rate}%, above the 5% warning level.",
                    "recommended_action": "Analyze failure reasons by payment method and gateway to identify specific issues.",
                    "priority": "medium",
                    "evidence_level": "moderate",
                }
            )

        # --- REVENUE GROWTH ---
        today = date.today()
        current_month_start = today.replace(day=1)
        prev_month_end = current_month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        current_rev = float(
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
                Transaction.transaction_date >= current_month_start,
            )
            .scalar()
        )
        prev_rev = float(
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_scenario == scenario,
                Transaction.status == "successful",
                Transaction.transaction_date >= prev_month_start,
                Transaction.transaction_date <= prev_month_end,
            )
            .scalar()
        )

        if prev_rev > 0:
            revenue_growth = round(((current_rev - prev_rev) / prev_rev) * 100, 2)
            if revenue_growth < -10:
                insight_id += 1
                insights.append(
                    {
                        "id": insight_id,
                        "business_problem": "Revenue Decline",
                        "metric": "revenue_growth_pct",
                        "observed_value": revenue_growth,
                        "threshold": -10.0,
                        "explanation": f"Month-over-month revenue has declined by {abs(revenue_growth)}%. "
                                       f"Current month: ${current_rev:,.2f} vs previous: ${prev_rev:,.2f}.",
                        "recommended_action": "Identify revenue drop causes — check for increased churn, reduced transaction volumes, "
                                              "or pricing changes. Launch promotional campaigns to recover lost revenue.",
                        "priority": "high",
                        "evidence_level": "strong",
                    }
                )

        # --- API PERFORMANCE ---
        avg_response = float(
            db.query(func.coalesce(func.avg(ApiLog.response_time_ms), 0))
            .filter(ApiLog.business_scenario == scenario)
            .scalar()
        )

        if avg_response > 1000:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "Slow API Performance",
                    "metric": "avg_response_time_ms",
                    "observed_value": round(avg_response, 2),
                    "threshold": 1000.0,
                    "explanation": f"Average API response time is {round(avg_response, 2)}ms, exceeding the 1000ms threshold. "
                                   "This may cause user experience degradation and increased abandonment.",
                    "recommended_action": "Profile slow endpoints, optimize database queries, consider caching strategies, "
                                          "and review infrastructure scaling.",
                    "priority": "high",
                    "evidence_level": "strong",
                }
            )
        elif avg_response > 500:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "API Response Time Warning",
                    "metric": "avg_response_time_ms",
                    "observed_value": round(avg_response, 2),
                    "threshold": 500.0,
                    "explanation": f"Average API response time is {round(avg_response, 2)}ms.",
                    "recommended_action": "Monitor performance trends and optimize endpoints approaching the threshold.",
                    "priority": "medium",
                    "evidence_level": "moderate",
                }
            )

        # --- API ERROR RATE ---
        total_api = (
            db.query(func.count(ApiLog.id))
            .filter(ApiLog.business_scenario == scenario)
            .scalar()
        )
        api_errors = (
            db.query(func.count(ApiLog.id))
            .filter(
                ApiLog.business_scenario == scenario,
                ApiLog.status_code >= 500,
            )
            .scalar()
        )
        api_error_rate = round((api_errors / total_api) * 100, 2) if total_api > 0 else 0.0

        if api_error_rate > 5:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "High Server Error Rate",
                    "metric": "5xx_error_rate",
                    "observed_value": api_error_rate,
                    "threshold": 5.0,
                    "explanation": f"Server error rate (5xx) is {api_error_rate}% ({api_errors} errors out of {total_api} requests).",
                    "recommended_action": "Investigate server errors by endpoint and error type. "
                                          "Review error logs, fix root causes, and implement circuit breakers.",
                    "priority": "high",
                    "evidence_level": "strong",
                }
            )

        # --- OPERATIONAL COST ---
        total_ops_cost = float(
            db.query(func.coalesce(func.sum(OperationalRecord.operational_cost), 0))
            .filter(OperationalRecord.business_scenario == scenario)
            .scalar()
        )

        total_ops = (
            db.query(func.count(OperationalRecord.id))
            .filter(OperationalRecord.business_scenario == scenario)
            .scalar()
        )

        failed_ops = (
            db.query(func.count(OperationalRecord.id))
            .filter(
                OperationalRecord.business_scenario == scenario,
                OperationalRecord.process_status == "failed",
            )
            .scalar()
        )
        ops_failure_rate = round((failed_ops / total_ops) * 100, 2) if total_ops > 0 else 0.0

        if ops_failure_rate > 15:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "High Operational Failure Rate",
                    "metric": "operational_failure_rate",
                    "observed_value": ops_failure_rate,
                    "threshold": 15.0,
                    "explanation": f"Operational process failure rate is {ops_failure_rate}% "
                                   f"({failed_ops} out of {total_ops} operations failed).",
                    "recommended_action": "Identify failing processes, implement monitoring and alerting, "
                                          "and address root causes through process automation.",
                    "priority": "high",
                    "evidence_level": "strong",
                }
            )

        # --- LOW PRODUCT ENGAGEMENT ---
        total_product_customers = total_customers or 1
        engaged_users = (
            db.query(func.count(func.distinct(ProductUsage.customer_id)))
            .filter(ProductUsage.business_scenario == scenario)
            .scalar()
        )
        engagement_rate = round((engaged_users / total_product_customers) * 100, 2) if total_product_customers > 0 else 0.0

        if engagement_rate < 30:
            insight_id += 1
            insights.append(
                {
                    "id": insight_id,
                    "business_problem": "Low Product Engagement",
                    "metric": "product_engagement_rate",
                    "observed_value": engagement_rate,
                    "threshold": 30.0,
                    "explanation": f"Only {engagement_rate}% of customers ({engaged_users} out of {total_product_customers}) "
                                   "are actively using the product.",
                    "recommended_action": "Improve onboarding flows, send feature discovery emails, "
                                          "and implement in-app guides to drive adoption.",
                    "priority": "medium",
                    "evidence_level": "moderate",
                }
            )

        # --- Sort by priority ---
        priority_order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return insights
