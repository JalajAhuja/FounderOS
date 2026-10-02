from founder.agent.corrective import build_corrective_plan


def test_any_evidence_missing_broadens_ticker_and_sources():

    correction = build_corrective_plan(
        {"ticker": "MSFT", "sources": ["qdrant"]},
        ["any_evidence"],
        "What was MSFT revenue in Q2 2025?",
    )

    assert correction["plan"]["ticker"] is None
    assert set(correction["plan"]["sources"]) == {
        "facts", "graph", "news", "qdrant",
    }
    assert "2025" not in correction["query"]
    assert "ticker_expansion" in correction["strategies"]
    assert "query_expansion" in correction["strategies"]


def test_prior_period_missing_adds_timeline_sources():

    correction = build_corrective_plan(
        {"ticker": "MSFT", "sources": ["qdrant"]},
        ["prior_period"],
        "What changed?",
    )

    assert "timeline" in correction["plan"]["sources"]
    assert "period_expansion" in correction["strategies"]


def test_external_event_missing_adds_news():

    correction = build_corrective_plan(
        {"sources": ["qdrant"]},
        ["external_event"],
        "What happened?",
    )

    assert "news" in correction["plan"]["sources"]


def test_financial_fact_missing_adds_facts():

    correction = build_corrective_plan(
        {"sources": ["qdrant"]},
        ["financial_fact"],
        "What was the revenue?",
    )

    assert "facts" in correction["plan"]["sources"]


def test_no_missing_signals_is_a_no_op():

    correction = build_corrective_plan(
        {"ticker": "MSFT", "sources": ["qdrant"]},
        [],
        "query",
    )

    assert correction["plan"]["sources"] == ["qdrant"]
    assert correction["query"] == "query"
    assert correction["strategies"] == []
