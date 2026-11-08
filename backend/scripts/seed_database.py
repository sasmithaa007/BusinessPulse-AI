"""
BusinessPulse AI — Database Seeding Script
==========================================
Standalone script that bootstraps the database and runs the DataGenerator
to populate all synthetic data tables.

Usage
-----
From the ``backend/`` directory:

    python scripts/seed_database.py

Environment variables (optional — defaults shown):
    DATABASE_URL   SQLAlchemy connection string
                   default: sqlite:///./businesspulse.db
    SEED_VALUE     NumPy random seed (integer)
                   default: 42
"""

from __future__ import annotations

import logging
import os
import sys
import time

# ---------------------------------------------------------------------------
# Make sure the project root (backend/) is on sys.path so that
# ``from app.xxx import yyy`` works when this script is executed directly.
# ---------------------------------------------------------------------------
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.services.data_generator import DataGenerator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("seed_database")

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./businesspulse.db",
)

SEED_VALUE: int = int(os.getenv("SEED_VALUE", "42"))

# SQLite-specific connect args (ignored for other engines)
_connect_args: dict = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)


def _create_session_factory(url: str) -> sessionmaker:
    """Create engine + session factory, importing ORM models first so that
    ``Base.metadata.create_all`` can discover all tables."""
    # Import Base and all models so metadata is populated
    try:
        from app.models import Base  # type: ignore[import]
    except ImportError as exc:
        logger.error(
            "Could not import app.models.Base — make sure all ORM models are "
            "defined and the project is on sys.path.  Detail: %s",
            exc,
        )
        raise

    engine = create_engine(
        url,
        connect_args=_connect_args,
        pool_pre_ping=True,
        echo=False,
    )

    logger.info("Connected to database: %s", url.split("@")[-1])  # hide credentials

    # Create all tables if they don't exist yet
    Base.metadata.create_all(bind=engine)
    logger.info("Schema verified / created.")

    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _ping_database(session_factory: sessionmaker) -> None:
    """Quick connectivity check before the long seeding run."""
    db = session_factory()
    try:
        db.execute(text("SELECT 1"))
        logger.info("Database ping: OK")
    finally:
        db.close()


def seed(database_url: str = DATABASE_URL, seed_value: int = SEED_VALUE) -> None:
    """
    Main seeding routine.

    Parameters
    ----------
    database_url:
        SQLAlchemy connection string.
    seed_value:
        NumPy random seed passed to :class:`~app.services.data_generator.DataGenerator`.
    """
    logger.info("=" * 60)
    logger.info("BusinessPulse AI — Database Seeder")
    logger.info("=" * 60)
    logger.info("DATABASE_URL : %s", database_url.split("@")[-1])
    logger.info("SEED_VALUE   : %d", seed_value)
    logger.info("-" * 60)

    session_factory = _create_session_factory(database_url)
    _ping_database(session_factory)

    db = session_factory()
    try:
        generator = DataGenerator(seed=seed_value)
        t0 = time.perf_counter()
        generator.generate_all_data(db)
        elapsed = time.perf_counter() - t0
        logger.info("-" * 60)
        logger.info("Seeding finished in %.2f seconds.", elapsed)
        logger.info("=" * 60)
    except Exception:
        logger.exception("Seeding failed — rolling back.")
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed the BusinessPulse AI database with synthetic data.",
    )
    parser.add_argument(
        "--database-url",
        default=DATABASE_URL,
        help=(
            "SQLAlchemy connection string.  "
            "Overrides the DATABASE_URL env-var.  "
            f"Default: {DATABASE_URL}"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED_VALUE,
        dest="seed_value",
        help=f"NumPy random seed for reproducibility.  Default: {SEED_VALUE}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help=(
            "Connect and verify the schema without inserting any rows.  "
            "Useful for CI health checks."
        ),
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("DRY RUN — schema check only, no data will be inserted.")
        session_factory = _create_session_factory(args.database_url)
        _ping_database(session_factory)
        logger.info("Dry run complete.")
        sys.exit(0)

    seed(database_url=args.database_url, seed_value=args.seed_value)
