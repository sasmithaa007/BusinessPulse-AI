"""
app/database/connection.py
--------------------------
SQLAlchemy engine, session factory, and FastAPI dependency for DB sessions.
"""

from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# ---------------------------------------------------------------------------
#  Engine
# ---------------------------------------------------------------------------

_connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite requires this flag when used with multiple threads (e.g. FastAPI)
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    # Echo SQL statements only in development to avoid log spam in production
    echo=settings.ENVIRONMENT == "development",
)

# ---------------------------------------------------------------------------
#  Session factory
# ---------------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ---------------------------------------------------------------------------
#  FastAPI dependency
# ---------------------------------------------------------------------------


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy :class:`Session` and guarantee it is closed after the
    request finishes, even if an exception is raised."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
