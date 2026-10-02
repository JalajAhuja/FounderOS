from founder.reasoning.dates import normalize_period, parse_date, quarter_from_month
from founder.retrieval.evidence import Evidence


def test_quarter_from_month():

    assert quarter_from_month(1) == 1
    assert quarter_from_month(4) == 2
    assert quarter_from_month(12) == 4


def test_parse_date_iso():

    assert parse_date("2025-06-01").year == 2025


def test_parse_date_rss_format():

    parsed = parse_date("Wed, 07 Jan 2026 08:00:00 GMT")

    assert parsed.year == 2026
    assert parsed.month == 1


def test_parse_date_invalid_returns_none():

    assert parse_date("not a date") is None
    assert parse_date(None) is None


def test_normalize_period_prefers_fiscal_metadata():

    evidence = Evidence(
        evidence_id="fact:1",
        source="XBRL",
        text="...",
        published_at="2025-08-01",
        metadata={"fiscal_year": 2025, "fiscal_period": "Q2"},
    )

    result = normalize_period(evidence)

    assert result == {
        "period": "2025-Q2",
        "basis": "fiscal",
        "year": 2025,
        "quarter": 2,
    }


def test_normalize_period_falls_back_to_published_at():

    evidence = Evidence(
        evidence_id="news:1",
        source="News",
        text="...",
        published_at="2025-11-01",
    )

    result = normalize_period(evidence)

    assert result["basis"] == "published_at"
    assert result["period"] == "2025-Q4"


def test_normalize_period_unknown_when_no_dates():

    evidence = Evidence(
        evidence_id="x:1",
        source="Qdrant",
        text="...",
    )

    assert normalize_period(evidence)["period"] == "unknown"
