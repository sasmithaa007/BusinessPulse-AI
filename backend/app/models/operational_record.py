"""
app/models/operational_record.py
---------------------------------
SQLAlchemy ORM model for operational process metrics.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class OperationalRecord(Base):
    """Captures operational process performance and cost data."""

    __tablename__ = "operational_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    process_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    processing_time_seconds: Mapped[float] = mapped_column(
        Numeric(8, 3), nullable=False, default=0.0
    )
    operational_cost: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0.0
    )

    # success | failed | running
    process_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="success"
    )

    recorded_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)

    # fintech | saas | developer_tools
    business_scenario: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<OperationalRecord id={self.id} process={self.process_name!r} "
            f"status={self.process_status!r} date={self.recorded_date}>"
        )
