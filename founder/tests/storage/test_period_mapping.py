"""Unit tests for fiscal period resolution."""

from founder.storage.period_mapping import (
    resolve_fiscal_period,
    _month_to_quarter,
)


def test_resolve_fiscal_period_with_calendar():

    result = resolve_fiscal_period("MSFT", "2025-06-30")

    assert result["fiscal_year"] == 2025
    assert result["basis"] == "fiscal_calendar"
    assert "Q" in result["canonical"]


def test_resolve_fiscal_period_fy_end_june():

    result = resolve_fiscal_period("MSFT", "2025-05-31")

    assert result["fiscal_year"] == 2025

    result2 = resolve_fiscal_period("MSFT", "2025-06-30")

    assert result2["fiscal_year"] == 2025


def test_resolve_fiscal_period_no_calendar():

    result = resolve_fiscal_period("UNKNOWN_TICKER", "2025-06-15")

    assert result["basis"] == "published_at"
    assert result["fiscal_year"] == 2025


def test_resolve_fiscal_period_invalid_date():

    result = resolve_fiscal_period("MSFT", "invalid")

    assert result["basis"] == "unknown"
    assert result["fiscal_year"] is None


def test_resolve_fiscal_period_none_date():

    result = resolve_fiscal_period("MSFT", None)

    assert result["basis"] == "unknown"


def test_month_to_quarter_calendar_year():

    # Calendar year (fy_end_month=12): Q1=Jan-Mar, Q2=Apr-Jun, etc.
    assert _month_to_quarter(1, 12) == 1
    assert _month_to_quarter(3, 12) == 1
    assert _month_to_quarter(4, 12) == 2
    assert _month_to_quarter(12, 12) == 4


def test_month_to_quarter_june_fiscal_year():

    # June fiscal year end (MSFT): Q4=Apr-Jun, Q1=Jul-Sep, etc.
    assert _month_to_quarter(6, 6) == 4  # June -> Q4 (fiscal year end)
    assert _month_to_quarter(7, 6) == 1  # July -> Q1
    assert _month_to_quarter(4, 6) == 4  # April -> Q4
