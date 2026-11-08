"""
backend/tests/test_auth.py
--------------------------
Pytest tests for user registration, login, and authorization.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "demo_account" in data


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_login_demo_admin():
    response = client.post(
        "/api/auth/login",
        json={
            "email": settings.DEMO_ADMIN_EMAIL,
            "password": settings.DEMO_ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401


def test_register_and_get_me():
    import uuid

    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Test Analyst",
            "email": unique_email,
            "password": "ValidPassword123!",
        },
    )
    assert reg_response.status_code == 201
    user_data = reg_response.json()
    assert user_data["email"] == unique_email

    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": unique_email,
            "password": "ValidPassword123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Access /api/auth/me
    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == unique_email


def test_unauthorized_access():
    response = client.get("/api/dashboard/summary?scenario=fintech")
    assert response.status_code == 401 or response.status_code == 403
