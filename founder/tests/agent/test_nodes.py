from founder.agent import nodes
from founder.agent.state import initial_state
from founder.retrieval.evidence import Evidence


def _evidence(
    evidence_id,
    source,
    section=None,
    published_at=None,
    score=1.0,
    text=None,
    ticker=None,
):

    return Evidence(
        evidence_id=evidence_id,
        source=source,
        text=text or f"text for {evidence_id}",
        score=score,
        section=section,
        published_at=published_at,
        ticker=ticker,
    )


def test_plan_retrieval_node_builds_deterministic_plan(monkeypatch):

    class FakeBundle:
        known_tickers = ["MSFT"]

    monkeypatch.setattr(
        nodes.tools,
        "get_bundle",
        lambda: FakeBundle(),
    )

    state = initial_state(
        "What was Microsoft's revenue in fiscal 2025?"
    )

    result = nodes.plan_retrieval_node(state)

    assert result["query_plan"]["intent"] == "factual"
    assert result["query_plan"]["sources"] == ["facts"]


def test_grade_evidence_sufficient_when_evidence_present():

    state = initial_state("q")
    state["evidence"] = [_evidence("e1", "Qdrant")]

    result = nodes.grade_evidence_node(state)

    assert result["sufficiency"]["sufficient"] is True
    assert result["sufficiency"]["evidence_count"] == 1


def test_grade_evidence_insufficient_when_empty():

    state = initial_state("q")

    result = nodes.grade_evidence_node(state)

    assert result["sufficiency"]["sufficient"] is False
    assert "No evidence retrieved." in result["sufficiency"]["reason"]


def test_normalize_evidence_dedupes_and_sorts():

    state = initial_state("q")

    state["evidence"] = [
        _evidence("e1", "Qdrant", score=0.5),
        _evidence("e1", "Qdrant", score=0.5),
        _evidence("e2", "XBRL", score=0.9),
    ]

    result = nodes.normalize_evidence_node(state)

    ids = [item.evidence_id for item in result["evidence"]]

    assert ids == ["e2", "e1"]


def test_temporal_reasoning_groups_by_year():

    state = initial_state("q")

    state["evidence"] = [
        _evidence("e1", "Qdrant", published_at="2025-06-01"),
        _evidence("e2", "Qdrant", published_at="2025-09-01"),
        _evidence("e3", "XBRL", published_at="2026-01-01"),
    ]

    result = nodes.temporal_reasoning_node(state)

    assert result["temporal_context"]["periods_observed"] == {
        "2025": 2,
        "2026": 1,
    }
    assert result["temporal_context"]["distinct_periods"] == 2


def test_contradiction_check_flags_same_period_polarity_conflict():

    state = initial_state("q")

    state["evidence"] = [
        _evidence(
            "e1",
            "Qdrant",
            section="AI monetization",
            ticker="MSFT",
            published_at="2025-06-01",
            text="Demand for our AI products is accelerating strongly.",
        ),
        _evidence(
            "e2",
            "News",
            section="AI monetization",
            ticker="MSFT",
            published_at="2025-06-15",
            text="Analysts note demand remains weak and uncertain.",
        ),
    ]

    result = nodes.contradiction_check_node(state)

    assert len(result["contradictions"]) == 1
    assert result["contradictions"][0]["type"] == "direct_conflict"


def test_synthesize_node_returns_fallback_without_evidence():

    state = initial_state("q")

    result = nodes.synthesize_node(state)

    assert "don't have enough evidence" in result["answer"]
    assert result["citations"] == []
