"""
backend/tests/test_dashboard.py
-------------------------------
Pytest tests for dashboard summary and trend endpoints.
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


def test_dashboard_summary():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/dashboard/summary?scenario=fintech", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "scenario" in data
    assert "customers" in data
    assert "revenue" in data


def test_dashboard_revenue_trend():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/dashboard/revenue-trend?scenario=fintech", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) or isinstance(data, dict)


def test_dashboard_scenarios():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    for scenario in ["fintech", "saas", "developer_tools"]:
        res = client.get(f"/api/dashboard/summary?scenario={scenario}", headers=headers)
        assert res.status_code == 200
