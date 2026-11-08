"""
backend/tests/run_tests.py
--------------------------
Comprehensive test runner for BusinessPulse AI backend API & Analytics.
Executes with lifespan context manager to initialize tables and seed data.
"""

import sys
import unittest
from starlette.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, ".")

from main import app
from app.core.config import settings


class TestBusinessPulseAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Enter TestClient lifespan context to trigger DB tables creation & admin seeding
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

        # Authenticate demo admin to acquire JWT
        res = cls.client.post(
            "/api/auth/login",
            json={
                "email": settings.DEMO_ADMIN_EMAIL,
                "password": settings.DEMO_ADMIN_PASSWORD,
            },
        )
        assert res.status_code == 200, f"Login failed: {res.text}"
        cls.token = res.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)

    def test_01_root_and_health(self):
        r_root = self.client.get("/")
        self.assertEqual(r_root.status_code, 200)
        self.assertEqual(r_root.json()["status"], "online")

        r_health = self.client.get("/health")
        self.assertEqual(r_health.status_code, 200)
        self.assertEqual(r_health.json()["status"], "healthy")

    def test_02_auth_me(self):
        res = self.client.get("/api/auth/me", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], settings.DEMO_ADMIN_EMAIL)

    def test_03_dashboard_summary_all_scenarios(self):
        for sc in ["fintech", "saas", "developer_tools"]:
            res = self.client.get(f"/api/dashboard/summary?scenario={sc}", headers=self.headers)
            self.assertEqual(res.status_code, 200, f"Failed for scenario {sc}: {res.text}")
            data = res.json()
            self.assertIn("customers", data)
            self.assertIn("revenue", data)

    def test_04_revenue_trends_and_leakage(self):
        res_trend = self.client.get("/api/revenue/trend?scenario=fintech", headers=self.headers)
        self.assertEqual(res_trend.status_code, 200)

        res_leak = self.client.get("/api/revenue/leakage?scenario=fintech", headers=self.headers)
        self.assertEqual(res_leak.status_code, 200)

    def test_05_customer_directory_and_filter(self):
        res = self.client.get("/api/customers?scenario=fintech&limit=5", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        items = res.json().get("items", [])
        self.assertTrue(len(items) <= 5)

        res_act = self.client.get("/api/customers?scenario=fintech&status=active&limit=5", headers=self.headers)
        self.assertEqual(res_act.status_code, 200)

    def test_06_churn_and_retention(self):
        res_churn = self.client.get("/api/customers/churn?scenario=fintech", headers=self.headers)
        self.assertEqual(res_churn.status_code, 200)

        res_ret = self.client.get("/api/customers/retention?scenario=fintech", headers=self.headers)
        self.assertEqual(res_ret.status_code, 200)

    def test_07_transactions_and_failures(self):
        res_sum = self.client.get("/api/transactions/summary?scenario=fintech", headers=self.headers)
        self.assertEqual(res_sum.status_code, 200)

        res_fail = self.client.get("/api/transactions/failures?scenario=fintech", headers=self.headers)
        self.assertEqual(res_fail.status_code, 200)

    def test_08_product_and_performance(self):
        res_prod = self.client.get("/api/products/usage?scenario=developer_tools", headers=self.headers)
        self.assertEqual(res_prod.status_code, 200)

        res_perf = self.client.get("/api/performance/summary?scenario=developer_tools", headers=self.headers)
        self.assertEqual(res_perf.status_code, 200)

    def test_09_operations_and_bottlenecks(self):
        res_ops = self.client.get("/api/operations/summary?scenario=fintech", headers=self.headers)
        self.assertEqual(res_ops.status_code, 200)

        res_bot = self.client.get("/api/operations/bottlenecks?scenario=fintech", headers=self.headers)
        self.assertEqual(res_bot.status_code, 200)

    def test_10_insights_engine(self):
        res = self.client.get("/api/insights?scenario=fintech", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        insights = data.get("insights", data) if isinstance(data, dict) else data
        self.assertIsInstance(insights, list)
        self.assertTrue(len(insights) > 0)


if __name__ == "__main__":
    unittest.main()
