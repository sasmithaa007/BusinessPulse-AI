"""
app/models/subscription.py
--------------------------
SQLAlchemy ORM model for customer subscriptions.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Subscription(Base):
    """Represents a subscription plan held by a customer."""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subscription_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    plan_name: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    annual_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    renewal_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # active | cancelled | expired | paused
    subscription_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )

    # fintech | saas | developer_tools
    business_scenario: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
    )

    # Relationships
    customer = relationship("Customer", backref="subscriptions", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Subscription id={self.id} code={self.subscription_code!r} "
            f"plan={self.plan_name!r} status={self.subscription_status!r}>"
        )
