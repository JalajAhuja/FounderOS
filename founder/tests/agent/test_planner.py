from founder.agent.planner import (
    INTENT_FACTUAL,
    INTENT_RELATIONSHIP,
    INTENT_SEMANTIC,
    INTENT_STRATEGIC,
    INTENT_TEMPORAL,
    build_retrieval_plan,
)


KNOWN_TICKERS = ["MSFT"]


def test_factual_query_plan():

    plan = build_retrieval_plan(
        "What was Microsoft's revenue in fiscal 2025?",
        known_tickers=KNOWN_TICKERS,
    )

    assert plan["intent"] == INTENT_FACTUAL
    assert plan["sources"] == ["facts"]


def test_semantic_query_plan():

    plan = build_retrieval_plan(
        "What did management say about AI monetization?",
        known_tickers=KNOWN_TICKERS,
    )

    assert plan["intent"] == INTENT_SEMANTIC
    assert plan["sources"] == ["qdrant"]


def test_relationship_query_plan():

    plan = build_retrieval_plan(
        "Which companies does Microsoft compete with?",
        known_tickers=KNOWN_TICKERS,
    )

    assert plan["intent"] == INTENT_RELATIONSHIP
    assert plan["sources"] == ["graph"]


def test_temporal_query_plan():

    plan = build_retrieval_plan(
        "What changed in Microsoft's AI strategy between Q2 2025 and Q1 2026?",
        known_tickers=KNOWN_TICKERS,
    )

    assert plan["intent"] == INTENT_TEMPORAL
    assert plan["needs_temporal_comparison"] is True
    assert plan["sources"] == ["graph", "qdrant", "timeline"]


def test_strategic_query_plan_with_external_events():

    plan = build_retrieval_plan(
        "What risks could AI infrastructure spending announcements create?",
        known_tickers=KNOWN_TICKERS,
    )

    assert plan["intent"] == INTENT_STRATEGIC
    assert plan["needs_external_events"] is True
    assert plan["sources"] == ["facts", "graph", "news", "qdrant"]


def test_plan_is_deterministic():

    query = "What changed in Microsoft's AI strategy between Q2 2025 and Q1 2026?"

    first = build_retrieval_plan(query, known_tickers=KNOWN_TICKERS)
    second = build_retrieval_plan(query, known_tickers=KNOWN_TICKERS)

    assert first == second
