from founder.agent.sufficiency import assess_sufficiency
from founder.retrieval.evidence import Evidence


def _evidence(evidence_id, ticker="MSFT", source="Qdrant", document_type=None):

    return Evidence(
        evidence_id=evidence_id,
        source=source,
        text="text",
        ticker=ticker,
        document_type=document_type,
        published_at="2025-06-01",
    )


def test_insufficient_when_no_evidence():

    result = assess_sufficiency({}, [])

    assert result["sufficient"] is False
    assert "any_evidence" in result["missing"]


def test_sufficient_with_simple_semantic_plan():

    result = assess_sufficiency(
        {"ticker": "MSFT"},
        [_evidence("e1")],
    )

    assert result["sufficient"] is True


def test_insufficient_when_temporal_comparison_needs_two_periods():

    result = assess_sufficiency(
        {"needs_temporal_comparison": True},
        [_evidence("e1")],
    )

    assert result["sufficient"] is False
    assert "prior_period" in result["missing"]


def test_insufficient_when_external_events_needed_but_no_news():

    result = assess_sufficiency(
        {"needs_external_events": True},
        [_evidence("e1", source="Qdrant")],
    )

    assert result["sufficient"] is False
    assert "external_event" in result["missing"]


def test_insufficient_when_fact_needed_but_no_financial_fact():

    result = assess_sufficiency(
        {"is_fact": True},
        [_evidence("e1", source="Qdrant")],
    )

    assert result["sufficient"] is False
    assert "financial_fact" in result["missing"]
