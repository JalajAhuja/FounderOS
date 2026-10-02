"""Unit tests for export serialization."""

import json
from founder.export.serialization import (
    serialize_evidence,
    serialize_answer,
    serialize_full_response,
)
from founder.retrieval.evidence import Evidence
from founder.generation.schemas import Claim, Citation, GeneratedAnswer


def test_serialize_evidence():

    evidence = Evidence(
        evidence_id="e1",
        source="Qdrant",
        text="test text",
        score=0.95,
        ticker="MSFT",
        published_at="2025-06-01",
    )

    serialized = serialize_evidence(evidence)

    assert serialized["evidence_id"] == "e1"
    assert serialized["source"] == "Qdrant"
    assert serialized["score"] == 0.95


def test_serialize_answer():

    answer = GeneratedAnswer(
        answer="Test answer.",
        claims=[
            Claim(
                text="A claim.",
                evidence_ids=["e1"],
                claim_type="source_claim",
                confidence=0.9,
            )
        ],
        citations=[
            Citation(
                citation_id=1,
                evidence_id="e1",
                citation_text="[1]",
                source="Qdrant",
                date="2025-06-01",
            )
        ],
    )

    serialized = serialize_answer(answer)

    assert serialized["text"] == "Test answer."
    assert len(serialized["claims"]) == 1
    assert len(serialized["citations"]) == 1


def test_serialize_full_response_is_valid_json():

    evidence = [
        Evidence(
            evidence_id="e1",
            source="Qdrant",
            text="text",
            score=0.9,
            ticker="MSFT",
        )
    ]

    answer = GeneratedAnswer(
        answer="Answer",
        claims=[],
        citations=[],
    )

    json_str = serialize_full_response(
        query="q",
        trace_id="t1",
        answer=answer,
        evidence=evidence,
    )

    # Must be valid JSON.
    parsed = json.loads(json_str)

    assert parsed["trace_id"] == "t1"
    assert parsed["query"] == "q"
    assert "answer" in parsed
    assert "evidence" in parsed


def test_serialize_deterministic_with_same_inputs():

    evidence = [
        Evidence(evidence_id="e1", source="Qdrant", text="t", score=0.9)
    ]

    answer = GeneratedAnswer(answer="a", claims=[], citations=[])

    json1 = serialize_full_response(
        query="q", trace_id="t1", answer=answer, evidence=evidence
    )

    json2 = serialize_full_response(
        query="q", trace_id="t1", answer=answer, evidence=evidence
    )

    assert json1 == json2
