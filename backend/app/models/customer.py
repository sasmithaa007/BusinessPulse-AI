"""
app/models/customer.py
----------------------
SQLAlchemy ORM model for business customers across all scenarios.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Customer(Base):
    """Represents a customer in any supported business scenario."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)

    # individual | business
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False, default="individual")

    # fintech | saas | developer_tools
    business_scenario: Mapped[str] = mapped_column(String(50), nullable=False)

    signup_date: Mapped[date] = mapped_column(Date, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="India")

    # active | inactive | churned
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # premium | standard | basic | enterprise
    segment: Mapped[str] = mapped_column(String(20), nullable=False, default="standard")

    lifetime_value: Mapped[float] = mapped_column(
        Numeric(14, 2), nullable=False, default=0.0
    )
    churn_risk_score: Mapped[float] = mapped_column(
        Numeric(5, 4), nullable=False, default=0.0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
    )

    __table_args__ = (
        Index("ix_customers_business_scenario", "business_scenario"),
        Index("ix_customers_status", "status"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Customer id={self.id} code={self.customer_code!r} "
            f"scenario={self.business_scenario!r}>"
        )
