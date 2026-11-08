"""
backend/tests/test_analytics.py
-------------------------------
Pytest tests for churn, retention, product, performance, operations, and insights.
"""

from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)


def get_auth_token():
    res = client.post(
        "/api/auth/login",
        json={
            "email": settings.DEMO_ADMIN_EMAIL,
            "password": settings.DEMO_ADMIN_PASSWORD,
        },
    )
    return res.json().get("access_token")


def test_churn_analytics():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/customers/churn?scenario=fintech", headers=headers)
    assert res.status_code == 200


def test_retention_analytics():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/customers/retention?scenario=saas", headers=headers)
    assert res.status_code == 200


def test_revenue_analytics():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/revenue/summary?scenario=fintech", headers=headers)
    assert res.status_code == 200


def test_performance_analytics():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/performance/summary?scenario=developer_tools", headers=headers)
    assert res.status_code == 200


def test_operations_analytics():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/operations/summary?scenario=fintech", headers=headers)
    assert res.status_code == 200


def test_insights():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/insights?scenario=fintech", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    assert isinstance(insights, list)
