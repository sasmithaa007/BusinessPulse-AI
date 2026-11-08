"""
app/schemas/auth.py
-------------------
Pydantic v2 schemas for authentication endpoints.
"""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserCreate(BaseModel):
    """Payload for registering a new user."""

    name: str = Field(..., min_length=2, max_length=255, examples=["Alice Smith"])
    email: str = Field(..., max_length=320, examples=["alice@example.com"])
    password: str = Field(..., min_length=8, max_length=128, examples=["Str0ng@Pass"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not EMAIL_REGEX.match(v_clean):
            raise ValueError("Invalid email format")
        return v_clean

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Payload for logging in."""

    email: str = Field(..., examples=["alice@example.com"])
    password: str = Field(..., examples=["Str0ng@Pass"])


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded inside a JWT token."""

    email: str | None = None


class UserOut(BaseModel):
    """Public representation of a user (never exposes password_hash)."""

    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
