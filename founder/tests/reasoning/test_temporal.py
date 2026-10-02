from founder.reasoning.temporal import (
    build_change_summary,
    compare_periods,
    detect_change,
    group_by_period,
)
from founder.retrieval.evidence import Evidence


def _fact(evidence_id, concept, value, fiscal_year, fiscal_period):

    return Evidence(
        evidence_id=evidence_id,
        source="XBRL",
        text=f"{concept}={value}",
        document_type="financial_fact",
        section=concept,
        metadata={
            "fiscal_year": fiscal_year,
            "fiscal_period": fiscal_period,
            "value": value,
        },
    )


def test_group_by_period_orders_chronologically():

    evidence = [
        _fact("f2", "Revenue", 200, 2026, "Q1"),
        _fact("f1", "Revenue", 100, 2025, "Q2"),
    ]

    groups = group_by_period(evidence)

    assert list(groups.keys()) == ["2025-Q2", "2026-Q1"]


def test_detect_change_reports_fact_value_delta():

    evidence_a = [_fact("f1", "Revenue", 100, 2025, "Q2")]
    evidence_b = [_fact("f2", "Revenue", 150, 2026, "Q1")]

    changes = detect_change(evidence_a, evidence_b)

    assert changes == [
        {
            "dimension": "Revenue",
            "before": 100,
            "after": 150,
            "evidence_ids": ["f1", "f2"],
        }
    ]


def test_compare_periods_builds_structured_summary():

    evidence = [
        _fact("f1", "Revenue", 100, 2025, "Q2"),
        _fact("f2", "Revenue", 150, 2026, "Q1"),
    ]

    result = compare_periods(evidence, "2025-Q2", "2026-Q1", topic="Revenue")

    assert result["period_a"] == "2025-Q2"
    assert result["period_b"] == "2026-Q1"
    assert result["changes"][0]["before"] == 100
    assert result["changes"][0]["after"] == 150


def test_build_change_summary_shape():

    summary = build_change_summary("AI", "2025-Q2", "2026-Q1", [])

    assert summary == {
        "topic": "AI",
        "period_a": "2025-Q2",
        "period_b": "2026-Q1",
        "changes": [],
    }
