"""Date/period parsing and normalization.

Rule: never assume publication date equals fiscal period. Prefer
fiscal_year/quarter metadata already carried on the evidence (present for
earnings/SEC chunks and XBRL facts) and only fall back to parsing
`published_at` when no fiscal metadata is available -- and label that
fallback so callers can distinguish an authoritative fiscal period from an
inferred one.
"""

import re
from datetime import datetime


DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%a, %d %b %Y %H:%M:%S %Z",
    "%Y",
]


def parse_date(value):

    if not value:
        return None

    text = str(value).strip()

    for fmt in DATE_FORMATS:

        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    # Last resort: pull a leading YYYY-MM-DD out of a longer string.
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)

    if match:

        try:
            return datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
            )
        except ValueError:
            return None

    return None


def quarter_from_month(month: int) -> int:

    return (month - 1) // 3 + 1


def normalize_period(evidence) -> dict:
    """Return `{"period": "2025-Q2", "basis": "fiscal" | "published_at" |
    "unknown", "year": 2025, "quarter": 2 | None}`.

    `basis="fiscal"` means the period came from explicit fiscal_year/
    fiscal_period or chunk year/quarter metadata (authoritative).
    `basis="published_at"` means it was inferred from the publication
    date, which is not guaranteed to match the fiscal reporting period.
    """

    metadata = evidence.metadata or {}

    fiscal_year = (
        metadata.get("fiscal_year")
        or metadata.get("year")
    )

    fiscal_period = (
        metadata.get("fiscal_period")
        or metadata.get("quarter")
    )

    if fiscal_year:

        quarter = None

        if fiscal_period:

            match = re.search(r"(\d)", str(fiscal_period))

            if match:
                quarter = int(match.group(1))

        period = (
            f"{fiscal_year}-Q{quarter}"
            if quarter
            else str(fiscal_year)
        )

        return {
            "period": period,
            "basis": "fiscal",
            "year": int(fiscal_year),
            "quarter": quarter,
        }

    parsed = parse_date(evidence.published_at)

    if parsed:

        quarter = quarter_from_month(parsed.month)

        return {
            "period": f"{parsed.year}-Q{quarter}",
            "basis": "published_at",
            "year": parsed.year,
            "quarter": quarter,
        }

    return {
        "period": "unknown",
        "basis": "unknown",
        "year": None,
        "quarter": None,
    }
