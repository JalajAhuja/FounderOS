"""Fiscal period resolution and harmonization."""

from datetime import datetime
from typing import Optional


FISCAL_CALENDARS = {
    "MSFT": {"fiscal_year_end_month": 6},
    "AAPL": {"fiscal_year_end_month": 9},
    "GOOGL": {"fiscal_year_end_month": 12},
    "AMZN": {"fiscal_year_end_month": 12},
    "META": {"fiscal_year_end_month": 12},
    "NVDA": {"fiscal_year_end_month": 1},
    "CRM": {"fiscal_year_end_month": 1},
    "DDOG": {"fiscal_year_end_month": 12},
    "SNOW": {"fiscal_year_end_month": 1},
    "PLTR": {"fiscal_year_end_month": 12},
    "SHOP": {"fiscal_year_end_month": 12},
    "NOW": {"fiscal_year_end_month": 12},
    "ADBE": {"fiscal_year_end_month": 12},
}


def resolve_fiscal_period(
    ticker: str | None,
    publication_date: str | None,
) -> dict:
    """Map a publication date to a canonical fiscal period.

    Returns:
        {
            "canonical": "FY2025-Q2" | "2025-Q2",
            "fiscal_year": 2025,
            "fiscal_quarter": 2,
            "basis": "fiscal_calendar" | "published_at" | "unknown"
        }
    """

    if not publication_date:
        return {
            "canonical": "unknown",
            "fiscal_year": None,
            "fiscal_quarter": None,
            "basis": "unknown",
        }

    try:
        parsed = datetime.fromisoformat(publication_date.replace(" ", "T"))
    except (ValueError, AttributeError):
        return {
            "canonical": "unknown",
            "fiscal_year": None,
            "fiscal_quarter": None,
            "basis": "unknown",
        }

    if ticker and ticker in FISCAL_CALENDARS:

        fy_end_month = FISCAL_CALENDARS[ticker]["fiscal_year_end_month"]

        if parsed.month <= fy_end_month:
            fiscal_year = parsed.year
        else:
            fiscal_year = parsed.year + 1

        fiscal_quarter = _month_to_quarter(parsed.month, fy_end_month)

        return {
            "canonical": f"{fiscal_year}-Q{fiscal_quarter}",
            "fiscal_year": fiscal_year,
            "fiscal_quarter": fiscal_quarter,
            "basis": "fiscal_calendar",
        }

    # Fallback: use published_at month to approximate quarter.
    fiscal_quarter = _month_to_quarter(parsed.month, 12)

    return {
        "canonical": f"{parsed.year}-Q{fiscal_quarter}",
        "fiscal_year": parsed.year,
        "fiscal_quarter": fiscal_quarter,
        "basis": "published_at",
    }


def _month_to_quarter(month: int, fy_end_month: int) -> int:
    """Map a month to a fiscal quarter (1-4).

    Assumes quarters are 3 months: Q1=end_month+1..+3, Q2=+4..+6, etc.,
    wrapping around so the fiscal-year-end month itself is Q4.
    """

    months_from_fy_end = (month - fy_end_month) % 12

    if months_from_fy_end == 0:
        return 4
    elif months_from_fy_end <= 3:
        return 1
    elif months_from_fy_end <= 6:
        return 2
    elif months_from_fy_end <= 9:
        return 3
    else:
        return 4
