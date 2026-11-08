"""
app/utils/validators.py
-----------------------
Input validation helpers for scenarios, date ranges, and uploaded files.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

ALLOWED_SCENARIOS = {"fintech", "saas", "developer_tools"}
ALLOWED_FILE_EXTENSIONS = {".csv"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_scenario(scenario: str) -> str:
    """Validate that the provided scenario is supported."""
    normalized = scenario.lower().strip()
    if normalized not in ALLOWED_SCENARIOS:
        raise ValueError(
            f"Invalid scenario '{scenario}'. Allowed scenarios: {', '.join(sorted(ALLOWED_SCENARIOS))}"
        )
    return normalized


def validate_date_range(
    start_date: Optional[date] = None, end_date: Optional[date] = None
) -> tuple[Optional[date], Optional[date]]:
    """Ensure start_date <= end_date."""
    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date cannot be greater than end_date")
    return start_date, end_date


def validate_csv_filename(filename: str) -> bool:
    """Ensure filename ends with .csv."""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_FILE_EXTENSIONS)
