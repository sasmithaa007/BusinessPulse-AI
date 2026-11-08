from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import date, timedelta
from app.models import Customer, Transaction


class CustomerAnalyticsService:

    @staticmethod
    def get_customers(
        db: Session,
        scenario: str,
        skip: int = 0,
        limit: int = 20,
        search: str = None,
        status: str = None,
        segment: str = None,
        sort_by: str = "signup_date",
        sort_order: str = "desc",
    ) -> dict:
        query = db.query(Customer).filter(Customer.business_scenario == scenario)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Customer.customer_code.ilike(search_term),
                )
            )

        if status:
            query = query.filter(Customer.status == status)

        if segment:
            query = query.filter(Customer.segment == segment)

        total = query.count()

        sort_column_map = {
            "signup_date": Customer.signup_date,
            "name": Customer.name,
            "lifetime_value": Customer.lifetime_value,
            "churn_risk_score": Customer.churn_risk_score,
            "status": Customer.status,
        }
        sort_col = sort_column_map.get(sort_by, Customer.signup_date)
        order_func = desc if sort_order == "desc" else asc
        query = query.order_by(order_func(sort_col))

        customers = query.offset(skip).limit(limit).all()

        items = []
        for c in customers:
            items.append(
                {
                    "id": c.id,
                    "customer_code": c.customer_code,
                    "name": c.name,
                    "email": c.email,
                    "customer_type": c.customer_type,
                    "signup_date": str(c.signup_date) if c.signup_date else None,
                    "country": c.country,
                    "status": c.status,
                    "segment": c.segment,
                    "lifetime_value": float(c.lifetime_value) if c.lifetime_value else 0.0,
                    "churn_risk_score": float(c.churn_risk_score) if c.churn_risk_score else 0.0,
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
    def get_customer_detail(db: Session, customer_id: int) -> dict:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None

        recent_transactions = (
            db.query(Transaction)
            .filter(Transaction.customer_id == customer_id)
            .order_by(desc(Transaction.transaction_date))
            .limit(10)
            .all()
        )

        txn_list = []
        for t in recent_transactions:
            txn_list.append(
                {
                    "id": t.id,
                    "transaction_code": t.transaction_code,
                    "transaction_date": str(t.transaction_date) if t.transaction_date else None,
                    "amount": float(t.amount) if t.amount else 0.0,
                    "currency": t.currency,
                    "status": t.status,
                    "payment_method": t.payment_method,
                    "failure_reason": t.failure_reason,
                    "gateway": t.gateway,
                    "processing_time_ms": float(t.processing_time_ms) if t.processing_time_ms else 0.0,
                }
            )

        total_spent = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.customer_id == customer_id,
                Transaction.status == "successful",
            )
            .scalar()
        )

        txn_count = (
            db.query(func.count(Transaction.id))
            .filter(Transaction.customer_id == customer_id)
            .scalar()
        )

        return {
            "id": customer.id,
            "customer_code": customer.customer_code,
            "name": customer.name,
            "email": customer.email,
            "customer_type": customer.customer_type,
            "business_scenario": customer.business_scenario,
            "signup_date": str(customer.signup_date) if customer.signup_date else None,
            "country": customer.country,
            "status": customer.status,
            "segment": customer.segment,
            "lifetime_value": float(customer.lifetime_value) if customer.lifetime_value else 0.0,
            "churn_risk_score": float(customer.churn_risk_score) if customer.churn_risk_score else 0.0,
            "total_spent": float(total_spent),
            "transaction_count": txn_count,
            "recent_transactions": txn_list,
        }

    @staticmethod
    def get_customer_summary(db: Session, scenario: str) -> dict:
        base = db.query(Customer).filter(Customer.business_scenario == scenario)

        total = base.count()
        active = base.filter(Customer.status == "active").count()
        inactive = base.filter(Customer.status == "inactive").count()
        churned = base.filter(Customer.status == "churned").count()

        avg_ltv = (
            db.query(func.coalesce(func.avg(Customer.lifetime_value), 0))
            .filter(Customer.business_scenario == scenario)
            .scalar()
        )

        avg_churn_risk = (
            db.query(func.coalesce(func.avg(Customer.churn_risk_score), 0))
            .filter(Customer.business_scenario == scenario)
            .scalar()
        )

        new_this_month = base.filter(
            Customer.signup_date >= date.today().replace(day=1)
        ).count()

        return {
            "total_customers": total,
            "active": active,
            "inactive": inactive,
            "churned": churned,
            "avg_lifetime_value": round(float(avg_ltv), 2),
            "avg_churn_risk_score": round(float(avg_churn_risk), 2),
            "new_this_month": new_this_month,
        }
