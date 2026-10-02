from founder.generation.citations import build_citations
from founder.retrieval.evidence import Evidence


def test_build_citations_assigns_stable_ids_in_first_appearance_order():

    evidence_by_id = {
        "e1": Evidence(evidence_id="e1", source="Qdrant", text="a", published_at="2025-01-01"),
        "e2": Evidence(evidence_id="e2", source="XBRL", text="b", published_at="2025-02-01"),
    }

    citations = build_citations(evidence_by_id, ["e2", "e1", "e2"])

    assert [c.citation_id for c in citations] == [1, 2]
    assert citations[0].evidence_id == "e2"
    assert citations[0].source == "XBRL"
    assert citations[1].evidence_id == "e1"


def test_build_citations_skips_unknown_evidence_ids():

    citations = build_citations({}, ["missing"])

    assert citations == []
