"""
app/utils/date_helpers.py
--------------------------
Date range and label utility functions used by analytics services.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta


def get_date_range(period: str) -> tuple[date, date]:
    """Return ``(start_date, end_date)`` for the given *period* string.

    Supported period keys
    ---------------------
    ``'7d'``   – last 7 calendar days (today inclusive)
    ``'30d'``  – last 30 calendar days
    ``'90d'``  – last 90 calendar days
    ``'180d'`` – last 180 calendar days
    ``'1y'``   – last 365 calendar days
    ``'all'``  – from 2020-01-01 to today (effectively "all data")

    Parameters
    ----------
    period:
        One of the keys listed above.  Case-insensitive.

    Returns
    -------
    tuple[date, date]
        ``(start_date, end_date)`` where both bounds are inclusive.

    Raises
    ------
    ValueError
        If *period* is not recognised.
    """
    today = date.today()
    period_lower = period.lower().strip()

    _deltas: dict[str, int] = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "180d": 180,
        "1y": 365,
    }

    if period_lower == "all":
        return date(2020, 1, 1), today

    if period_lower not in _deltas:
        raise ValueError(
            f"Unknown period {period!r}. "
            f"Valid values are: {', '.join(list(_deltas.keys()) + ['all'])}"
        )

    start = today - timedelta(days=_deltas[period_lower] - 1)
    return start, today


def get_month_label(d: date) -> str:
    """Return a human-readable month label for *d*, e.g. ``'Jan 2024'``.

    Parameters
    ----------
    d:
        Any :class:`datetime.date` or :class:`datetime.datetime` instance.

    Returns
    -------
    str
        A string in the format ``'Mon YYYY'``.
    """
    return d.strftime("%b %Y")


def months_between(start: date, end: date) -> int:
    """Return the number of whole calendar months between *start* and *end*.

    The count is computed by advancing the month / year counters independently
    of day-of-month, so ``months_between(date(2024, 1, 31), date(2024, 2, 28))``
    returns ``1``.

    Parameters
    ----------
    start:
        The earlier date.
    end:
        The later date.

    Returns
    -------
    int
        Number of whole months.  Returns 0 if *end* <= *start*.
    """
    if end <= start:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)


def iter_months(start: date, end: date):
    """Yield the first day of each calendar month from *start* to *end* inclusive.

    Useful for building time-series buckets.
    """
    current = start.replace(day=1)
    end_month = end.replace(day=1)
    while current <= end_month:
        yield current
        # Advance to first day of next month
        _, last_day = monthrange(current.year, current.month)
        current = (current + timedelta(days=last_day)).replace(day=1)
