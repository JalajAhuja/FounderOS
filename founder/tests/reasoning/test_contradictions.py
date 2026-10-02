from founder.reasoning.contradictions import detect_contradictions
from founder.retrieval.evidence import Evidence


def _evidence(evidence_id, source, text, ticker="MSFT", section="AI", published_at="2025-06-01"):

    return Evidence(
        evidence_id=evidence_id,
        source=source,
        text=text,
        ticker=ticker,
        section=section,
        published_at=published_at,
    )


def test_same_period_opposite_polarity_is_direct_conflict():

    evidence = [
        _evidence(
            "e1", "Qdrant",
            "Demand for our AI products is accelerating strongly.",
            published_at="2025-06-01",
        ),
        _evidence(
            "e2", "News",
            "Analysts note demand remains weak and uncertain.",
            published_at="2025-06-10",
        ),
    ]

    contradictions = detect_contradictions(evidence)

    assert len(contradictions) == 1
    assert contradictions[0]["type"] == "direct_conflict"
    assert contradictions[0]["time_relation"] == "same"


def test_different_quarter_opposite_polarity_is_change_over_time():

    evidence = [
        _evidence(
            "e1", "Qdrant",
            "Growth accelerated significantly this quarter.",
            published_at="2025-03-01",
        ),
        _evidence(
            "e2", "Qdrant",
            "Growth declined and demand weakened this quarter.",
            published_at="2025-10-01",
        ),
    ]

    contradictions = detect_contradictions(evidence)

    assert len(contradictions) == 1
    assert contradictions[0]["type"] == "change_over_time"


def test_no_conflict_when_no_polarity_keywords():

    evidence = [
        _evidence("e1", "Qdrant", "We discussed our roadmap for the year."),
        _evidence("e2", "News", "The company announced a new product."),
    ]

    assert detect_contradictions(evidence) == []


def test_no_conflict_across_different_sections():

    evidence = [
        _evidence("e1", "Qdrant", "Growth is accelerating.", section="AI"),
        _evidence("e2", "News", "Margins are declining.", section="Cloud"),
    ]

    assert detect_contradictions(evidence) == []
