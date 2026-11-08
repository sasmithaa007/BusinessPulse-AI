"""
app/models/product_usage.py
---------------------------
SQLAlchemy ORM model for product / feature usage events.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ProductUsage(Base):
    """Tracks how customers interact with individual product features."""

    __tablename__ = "product_usage"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    feature_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    usage_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    session_duration_minutes: Mapped[float] = mapped_column(
        Numeric(8, 2), nullable=False, default=0.0
    )

    # fintech | saas | developer_tools
    business_scenario: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
    )

    # Relationships
    customer = relationship("Customer", backref="product_usages", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ProductUsage id={self.id} customer_id={self.customer_id} "
            f"feature={self.feature_name!r} date={self.usage_date}>"
        )
