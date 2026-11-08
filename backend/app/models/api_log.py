"""
app/models/api_log.py
---------------------
SQLAlchemy ORM model for API request/response log entries.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ApiLog(Base):
    """Stores aggregated or sampled API request telemetry for the developer-tools scenario."""

    __tablename__ = "api_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False, index=True)

    # GET | POST | PUT | DELETE
    method: Mapped[str] = mapped_column(String(10), nullable=False)

    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    request_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    error_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # fintech | saas | developer_tools
    business_scenario: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ApiLog id={self.id} endpoint={self.endpoint!r} "
            f"status={self.status_code} date={self.request_date}>"
        )
