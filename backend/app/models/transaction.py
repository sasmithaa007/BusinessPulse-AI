"""
app/models/transaction.py
-------------------------
SQLAlchemy ORM model for financial transactions.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Transaction(Base):
    """Represents a single financial transaction linked to a customer."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transaction_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Default currency is INR
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    # success | failed | pending | refunded
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")

    # upi | netbanking | card | wallet | neft
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)

    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gateway: Mapped[str] = mapped_column(String(100), nullable=False)
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # fintech | saas | developer_tools
    business_scenario: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
    )

    # Relationships
    customer = relationship("Customer", backref="transactions", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Transaction id={self.id} code={self.transaction_code!r} "
            f"amount={self.amount} status={self.status!r}>"
        )
