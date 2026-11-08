"""
backend/tests/test_transactions.py
----------------------------------
Pytest tests for transaction endpoints.
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


def test_transactions_summary():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/transactions/summary?scenario=fintech", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_transactions" in data
    assert "success_rate" in data


def test_transactions_list():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/transactions?scenario=fintech&limit=10", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) <= 10


def test_transaction_failures():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/transactions/failures?scenario=fintech", headers=headers)
    assert res.status_code == 200
