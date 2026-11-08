"""
app/services/data_generator.py
------------------------------
Deterministic synthetic data generator for BusinessPulse AI.
Seed = 42 for reproducible demonstration in data analyst interviews.
Generates:
- 5,000 customers (FinTech, SaaS, Developer Tools)
- 5,000 subscriptions
- 20,000 financial transactions
- 15,000 product usage records
- 20,000 API logs
- 5,000 operational process records
"""

from __future__ import annotations

import logging
import random
from datetime import date, datetime, timedelta, timezone
from typing import List

import numpy as np
from sqlalchemy.orm import Session

from app.models import (
    Customer,
    Transaction,
    Subscription,
    ProductUsage,
    ApiLog,
    OperationalRecord,
)

logger = logging.getLogger("businesspulse.generator")

TOTAL_CUSTOMERS = 5000
TOTAL_SUBSCRIPTIONS = 5000
TOTAL_TRANSACTIONS = 20000
TOTAL_PRODUCT_USAGE = 15000
TOTAL_API_LOGS = 20000
TOTAL_OPERATIONAL_RECORDS = 5000

SCENARIOS = ["fintech", "saas", "developer_tools"]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Muhammad", "Sai",
    "Arnav", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharva", "Advik", "Pranav",
    "Advaith", "Aarush", "Dhruv", "Kabir", "Ritvik", "Darsh", "Kian", "Rudra",
    "Anaya", "Diya", "Saanvi", "Aanya", "Aadhya", "Pari", "Anika", "Navya",
    "Angel", "Isha", "Myra", "Avani", "Kiara", "Sara", "Riya", "Aarohi",
    "Anvi", "Trisha", "Vanya", "Aditi", "Mira", "Shanaya", "Sneha", "Kavya",
    "Pooja", "Rohan"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Mishra", "Joshi",
    "Jha", "Reddy", "Nair", "Iyer", "Rao", "Deshmukh", "Kulkarni", "Patil",
    "Mehta", "Shah", "Agarwal", "Bose", "Chatterjee", "Banerjee", "Mukherjee",
    "Dutta", "Das", "Ghosh", "Roy", "Sengupta", "Choudhury", "Bhattacharya",
    "Pandey", "Trivedi", "Shukla", "Dubey", "Chauhan", "Yadav", "Verma",
    "Chopra", "Malhotra", "Kapoor", "Khanna", "Bhatia", "Saxena", "Soni",
    "Bansal", "Goel", "Mittal", "Singhal", "Garg", "Jain"
]

PLANS = {
    "fintech": [
        ("Basic", 199.0, 1990.0),
        ("Pro", 499.0, 4990.0),
        ("Wealth", 999.0, 9990.0),
        ("Ultra", 1999.0, 19990.0),
    ],
    "saas": [
        ("Starter", 1499.0, 14990.0),
        ("Growth", 4999.0, 49990.0),
        ("Business", 12999.0, 129990.0),
        ("Enterprise", 29999.0, 299990.0),
    ],
    "developer_tools": [
        ("Free", 0.0, 0.0),
        ("Solo", 799.0, 7990.0),
        ("Team", 2499.0, 24990.0),
        ("Business", 7499.0, 74990.0),
    ],
}

FEATURES = {
    "fintech": ["Mutual Funds", "Equities Order Book", "SIP Automation", "Tax Harvesting", "Direct Gold"],
    "saas": ["Subscription Billing", "Tax Automation", "Invoice PDF Engine", "Webhook Dispatcher", "Audit Trail"],
    "developer_tools": ["API Collection Runner", "Mock Server Deploy", "Telemetry Monitor", "Team Workspaces", "CI/CD Webhook"],
}

ENDPOINTS = {
    "fintech": ["/api/portfolio", "/api/orders", "/api/payments", "/api/market_data", "/api/kyc"],
    "saas": ["/api/subscriptions", "/api/invoices", "/api/tax/compute", "/api/customers", "/api/webhooks"],
    "developer_tools": ["/api/collections/run", "/api/mock/deploy", "/api/environments", "/api/tests", "/api/monitors"],
}

PROCESS_NAMES = {
    "fintech": ["KYC_Verification", "Payment_Settlement", "Fraud_Detection_Scan", "Portfolio_Rebalancing", "Tax_Computation"],
    "saas": ["Invoice_Generation", "Subscription_Renewal", "Tax_Calculation", "Payment_Processing", "Audit_Export"],
    "developer_tools": ["Test_Collection_Exec", "Mock_Server_Deploy", "API_Telemetry_Sync", "Monitor_Health_Check", "Build_Pipeline"],
}

FAILURE_REASONS = [
    "Insufficient funds",
    "Bank network timeout",
    "Card declined by issuer",
    "Daily payment limit exceeded",
    "Invalid OTP / Authentication failure",
    "Payment gateway unreachable",
]


class DataGenerator:
    """Generates synthetic multi-scenario enterprise datasets."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        random.seed(seed)
        self.now = datetime.now(tz=timezone.utc)
        self.start_date = self.now.date() - timedelta(days=540)  # 18 months

    def generate_all_data(self, db: Session) -> None:
        """Seed all 6 operational and analytical tables in batch."""
        if db.query(Customer).count() > 0:
            logger.info("Database already seeded. Skipping generator.")
            return

        logger.info("Generating %d synthetic customers...", TOTAL_CUSTOMERS)
        customers = self._generate_customers(db)

        logger.info("Generating %d synthetic subscriptions...", TOTAL_SUBSCRIPTIONS)
        self._generate_subscriptions(db, customers)

        logger.info("Generating %d synthetic transactions...", TOTAL_TRANSACTIONS)
        self._generate_transactions(db, customers)

        logger.info("Generating %d synthetic product usage records...", TOTAL_PRODUCT_USAGE)
        self._generate_product_usage(db, customers)

        logger.info("Generating %d synthetic API telemetry logs...", TOTAL_API_LOGS)
        self._generate_api_logs(db)

        logger.info("Generating %d synthetic operational records...", TOTAL_OPERATIONAL_RECORDS)
        self._generate_operational_records(db)

        logger.info("All synthetic data successfully generated and committed.")

    def _generate_customers(self, db: Session) -> List[Customer]:
        customers = []
        statuses = ["active", "inactive", "churned"]
        status_weights = [0.72, 0.10, 0.18]
        segments = ["basic", "standard", "premium", "enterprise"]
        segment_weights = [0.40, 0.35, 0.18, 0.07]

        for i in range(TOTAL_CUSTOMERS):
            scenario = SCENARIOS[i % 3]
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            code = f"CUST-{scenario[:2].upper()}-{100000 + i}"
            email = f"{first.lower()}.{last.lower()}{i}@synthetic.demo"
            days_ago = int(self._rng.integers(10, 540))
            signup_date = self.start_date + timedelta(days=days_ago)

            status = random.choices(statuses, weights=status_weights)[0]
            segment = random.choices(segments, weights=segment_weights)[0]
            ltv = float(self._rng.uniform(1200, 150000)) if segment in ["premium", "enterprise"] else float(self._rng.uniform(200, 25000))
            churn_risk = float(self._rng.uniform(0.65, 0.98)) if status == "churned" else float(self._rng.uniform(0.02, 0.45))

            c = Customer(
                customer_code=code,
                name=name,
                email=email,
                customer_type="business" if segment == "enterprise" else "individual",
                business_scenario=scenario,
                signup_date=signup_date,
                country="India",
                status=status,
                segment=segment,
                lifetime_value=round(ltv, 2),
                churn_risk_score=round(churn_risk, 4),
            )
            customers.append(c)

        db.bulk_save_objects(customers)
        db.commit()

        # Query back customers to get auto-assigned primary keys
        return db.query(Customer).all()

    def _generate_subscriptions(self, db: Session, customers: List[Customer]) -> None:
        subscriptions = []
        sub_statuses = ["active", "cancelled", "expired", "paused"]
        sub_status_weights = [0.74, 0.16, 0.06, 0.04]

        for i in range(TOTAL_SUBSCRIPTIONS):
            customer = customers[i % len(customers)]
            scenario = customer.business_scenario
            plan_tuple = random.choice(PLANS[scenario])
            plan_name, monthly, annual = plan_tuple
            code = f"SUB-{scenario[:2].upper()}-{200000 + i}"

            start_d = customer.signup_date
            status = "cancelled" if customer.status == "churned" else random.choices(sub_statuses, weights=sub_status_weights)[0]

            s = Subscription(
                customer_id=customer.id,
                subscription_code=code,
                plan_name=plan_name,
                monthly_amount=monthly,
                annual_amount=annual,
                start_date=start_d,
                end_date=start_d + timedelta(days=365) if status in ["cancelled", "expired"] else None,
                renewal_date=start_d + timedelta(days=30),
                subscription_status=status,
                business_scenario=scenario,
            )
            subscriptions.append(s)

        db.bulk_save_objects(subscriptions)
        db.commit()

    def _generate_transactions(self, db: Session, customers: List[Customer]) -> None:
        transactions = []
        methods = {
            "fintech": ["upi", "netbanking", "card", "wallet"],
            "saas": ["card", "netbanking", "neft"],
            "developer_tools": ["card", "wallet", "neft"],
        }
        gateways = ["Razorpay", "Juspay", "Stripe", "Cashfree", "BillDesk"]

        for i in range(TOTAL_TRANSACTIONS):
            customer = customers[i % len(customers)]
            scenario = customer.business_scenario
            code = f"TXN-{1000000 + i}"
            days_ago = int(self._rng.integers(1, 540))
            txn_date = self.now - timedelta(days=days_ago, minutes=int(self._rng.integers(1, 1440)))

            # Fail rate ~15%
            is_failed = bool(self._rng.uniform(0, 1) < 0.15)
            is_pending = bool(not is_failed and self._rng.uniform(0, 1) < 0.04)
            status = "failed" if is_failed else ("pending" if is_pending else "success")

            failure_reason = random.choice(FAILURE_REASONS) if is_failed else None

            if scenario == "fintech":
                amount = float(self._rng.uniform(100, 75000))
            elif scenario == "saas":
                amount = float(self._rng.uniform(1499, 45000))
            else:
                amount = float(self._rng.uniform(499, 15000))

            t = Transaction(
                customer_id=customer.id,
                transaction_code=code,
                transaction_date=txn_date,
                amount=round(amount, 2),
                currency="INR",
                status=status,
                payment_method=random.choice(methods[scenario]),
                failure_reason=failure_reason,
                gateway=random.choice(gateways),
                processing_time_ms=int(self._rng.integers(80, 2400)),
                business_scenario=scenario,
            )
            transactions.append(t)

            if len(transactions) >= 5000:
                db.bulk_save_objects(transactions)
                db.commit()
                transactions = []

        if transactions:
            db.bulk_save_objects(transactions)
            db.commit()

    def _generate_product_usage(self, db: Session, customers: List[Customer]) -> None:
        usages = []
        for i in range(TOTAL_PRODUCT_USAGE):
            customer = customers[i % len(customers)]
            scenario = customer.business_scenario
            feature = random.choice(FEATURES[scenario])
            days_ago = int(self._rng.integers(1, 365))
            u_date = (self.now - timedelta(days=days_ago)).date()
            duration = float(self._rng.uniform(1.5, 45.0))
            count = int(self._rng.integers(1, 12))

            u = ProductUsage(
                customer_id=customer.id,
                feature_name=feature,
                usage_count=count,
                usage_date=u_date,
                session_duration_minutes=round(duration, 2),
                business_scenario=scenario,
            )
            usages.append(u)

            if len(usages) >= 5000:
                db.bulk_save_objects(usages)
                db.commit()
                usages = []

        if usages:
            db.bulk_save_objects(usages)
            db.commit()

    def _generate_api_logs(self, db: Session) -> None:
        logs = []
        methods = ["GET", "POST", "PUT", "DELETE"]

        for i in range(TOTAL_API_LOGS):
            scenario = SCENARIOS[i % 3]
            endpoint = random.choice(ENDPOINTS[scenario])
            method = random.choices(methods, weights=[0.65, 0.25, 0.08, 0.02])[0]

            # 94% normal latency (50-400ms), 5% slow (400-2000ms), 1% critical (>2000ms)
            roll = float(self._rng.uniform(0, 1))
            if roll < 0.94:
                resp_time = int(self._rng.integers(50, 400))
                status_code = 200
                error_type = None
            elif roll < 0.99:
                resp_time = int(self._rng.integers(400, 2000))
                status_code = random.choice([200, 400, 429])
                error_type = "RateLimitWarning" if status_code == 429 else None
            else:
                resp_time = int(self._rng.integers(2000, 4500))
                status_code = random.choice([500, 502, 504])
                error_type = "GatewayTimeoutError"

            days_ago = int(self._rng.integers(1, 90))
            req_date = self.now - timedelta(days=days_ago, minutes=int(self._rng.integers(1, 1440)))

            l = ApiLog(
                endpoint=endpoint,
                method=method,
                response_time_ms=resp_time,
                status_code=status_code,
                request_date=req_date,
                error_type=error_type,
                user_agent="BusinessPulse-Agent/1.0",
                business_scenario=scenario,
            )
            logs.append(l)

            if len(logs) >= 5000:
                db.bulk_save_objects(logs)
                db.commit()
                logs = []

        if logs:
            db.bulk_save_objects(logs)
            db.commit()

    def _generate_operational_records(self, db: Session) -> None:
        records = []
        depts = ["Operations", "Settlement", "Engineering", "Compliance", "Finance"]

        for i in range(TOTAL_OPERATIONAL_RECORDS):
            scenario = SCENARIOS[i % 3]
            process = random.choice(PROCESS_NAMES[scenario])
            time_sec = float(self._rng.uniform(0.8, 18.5))
            cost = float(self._rng.uniform(500, 15000))
            is_failed = bool(self._rng.uniform(0, 1) < 0.11)
            days_ago = int(self._rng.integers(1, 180))
            rec_date = (self.now - timedelta(days=days_ago)).date()

            rec = OperationalRecord(
                process_name=process,
                processing_time_seconds=round(time_sec, 3),
                operational_cost=round(cost, 2),
                process_status="failed" if is_failed else "success",
                recorded_date=rec_date,
                department=random.choice(depts),
                business_scenario=scenario,
            )
            records.append(rec)

            if len(records) >= 5000:
                db.bulk_save_objects(records)
                db.commit()
                records = []

        if records:
            db.bulk_save_objects(records)
            db.commit()
