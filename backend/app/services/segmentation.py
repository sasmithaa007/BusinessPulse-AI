from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import date, timedelta
from app.models import Customer, Transaction


class SegmentationService:

    @staticmethod
    def get_segment_distribution(db: Session, scenario: str) -> list:
        results = (
            db.query(
                Customer.segment,
                func.count(Customer.id).label("count"),
            )
            .filter(Customer.business_scenario == scenario)
            .group_by(Customer.segment)
            .order_by(func.count(Customer.id).desc())
            .all()
        )

        total = sum(row.count for row in results)

        segments = []
        for row in results:
            count = row.count or 0
            pct = round((count / total) * 100, 2) if total > 0 else 0.0
            segments.append(
                {
                    "segment": row.segment or "Unknown",
                    "count": count,
                    "percentage": pct,
                }
            )

        return segments

    @staticmethod
    def get_segment_value(db: Session, scenario: str) -> list:
        results = (
            db.query(
                Customer.segment,
                func.count(Customer.id).label("customer_count"),
                func.coalesce(func.avg(Customer.lifetime_value), 0).label("avg_ltv"),
                func.coalesce(func.sum(Customer.lifetime_value), 0).label("total_ltv"),
            )
            .filter(Customer.business_scenario == scenario)
            .group_by(Customer.segment)
            .all()
        )

        segment_ids = {}
        for row in results:
            segment_ids[row.segment] = row

        revenue_data = (
            db.query(
                Customer.segment,
                func.coalesce(func.sum(Transaction.amount), 0).label("total_revenue"),
                func.coalesce(func.avg(Transaction.amount), 0).label("avg_txn_value"),
                func.count(Transaction.id).label("txn_count"),
            )
            .join(Transaction, Transaction.customer_id == Customer.id)
            .filter(
                Customer.business_scenario == scenario,
                Transaction.status == "successful",
            )
            .group_by(Customer.segment)
            .all()
        )

        revenue_map = {}
        for row in revenue_data:
            revenue_map[row.segment] = {
                "total_revenue": round(float(row.total_revenue), 2),
                "avg_txn_value": round(float(row.avg_txn_value), 2),
                "txn_count": row.txn_count,
            }

        output = []
        for row in results:
            rev = revenue_map.get(row.segment, {"total_revenue": 0.0, "avg_txn_value": 0.0, "txn_count": 0})
            customer_count = row.customer_count or 0
            rev_per_customer = round(rev["total_revenue"] / customer_count, 2) if customer_count > 0 else 0.0
            output.append(
                {
                    "segment": row.segment or "Unknown",
                    "customer_count": customer_count,
                    "avg_lifetime_value": round(float(row.avg_ltv), 2),
                    "total_lifetime_value": round(float(row.total_ltv), 2),
                    "total_revenue": rev["total_revenue"],
                    "avg_transaction_value": rev["avg_txn_value"],
                    "transaction_count": rev["txn_count"],
                    "revenue_per_customer": rev_per_customer,
                }
            )

        return output

    @staticmethod
    def get_rfm_analysis(db: Session, scenario: str) -> list:
        today = date.today()

        customers = (
            db.query(Customer)
            .filter(Customer.business_scenario == scenario)
            .all()
        )

        if not customers:
            return []

        customer_ids = [c.id for c in customers]

        txn_data = (
            db.query(
                Transaction.customer_id,
                func.max(Transaction.transaction_date).label("last_txn_date"),
                func.count(Transaction.id).label("frequency"),
                func.coalesce(func.sum(Transaction.amount), 0).label("monetary"),
            )
            .filter(
                Transaction.customer_id.in_(customer_ids),
                Transaction.status == "successful",
            )
            .group_by(Transaction.customer_id)
            .all()
        )

        txn_map = {}
        for row in txn_data:
            last_date = row.last_txn_date
            if last_date:
                if hasattr(last_date, 'date'):
                    recency_days = (today - last_date.date()).days
                else:
                    recency_days = (today - last_date).days
            else:
                recency_days = 9999
            txn_map[row.customer_id] = {
                "recency_days": recency_days,
                "frequency": row.frequency or 0,
                "monetary": float(row.monetary) if row.monetary else 0.0,
            }

        all_recency = []
        all_frequency = []
        all_monetary = []

        for c in customers:
            data = txn_map.get(c.id, {"recency_days": 9999, "frequency": 0, "monetary": 0.0})
            all_recency.append(data["recency_days"])
            all_frequency.append(data["frequency"])
            all_monetary.append(data["monetary"])

        def score_quintile(values: list, value: float, reverse: bool = False) -> int:
            sorted_vals = sorted(set(values))
            if len(sorted_vals) == 0:
                return 3
            n = len(sorted_vals)
            thresholds = [sorted_vals[int(n * i / 5)] for i in range(1, 5)]
            if reverse:
                if value <= thresholds[0]:
                    return 5
                elif value <= thresholds[1]:
                    return 4
                elif value <= thresholds[2]:
                    return 3
                elif value <= thresholds[3]:
                    return 2
                else:
                    return 1
            else:
                if value <= thresholds[0]:
                    return 1
                elif value <= thresholds[1]:
                    return 2
                elif value <= thresholds[2]:
                    return 3
                elif value <= thresholds[3]:
                    return 4
                else:
                    return 5

        rfm_results = []
        for c in customers:
            data = txn_map.get(c.id, {"recency_days": 9999, "frequency": 0, "monetary": 0.0})

            r_score = score_quintile(all_recency, data["recency_days"], reverse=True)
            f_score = score_quintile(all_frequency, data["frequency"], reverse=False)
            m_score = score_quintile(all_monetary, data["monetary"], reverse=False)

            rfm_total = r_score + f_score + m_score

            if rfm_total >= 13:
                rfm_label = "Champions"
            elif rfm_total >= 10:
                rfm_label = "Loyal Customers"
            elif rfm_total >= 8:
                rfm_label = "Potential Loyalists"
            elif rfm_total >= 6:
                rfm_label = "At Risk"
            elif rfm_total >= 4:
                rfm_label = "Needs Attention"
            else:
                rfm_label = "Lost"

            rfm_results.append(
                {
                    "customer_id": c.id,
                    "customer_name": c.name,
                    "segment": c.segment,
                    "recency_days": data["recency_days"],
                    "frequency": data["frequency"],
                    "monetary": round(data["monetary"], 2),
                    "r_score": r_score,
                    "f_score": f_score,
                    "m_score": m_score,
                    "rfm_score": rfm_total,
                    "rfm_segment": rfm_label,
                }
            )

        rfm_results.sort(key=lambda x: x["rfm_score"], reverse=True)
        return rfm_results
