"""
backend/tests/test_customers.py
-------------------------------
Pytest tests for customer listing, filtering, and detail endpoints.
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


def test_list_customers():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/customers?scenario=fintech&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 10


def test_customer_filtering():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/customers?scenario=fintech&status=active&limit=5", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "active"
