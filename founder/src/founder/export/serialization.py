"""Deterministic JSON serialization for answers, evidence, and traces."""

import json
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from founder.retrieval.evidence import Evidence
    from founder.generation.schemas import GeneratedAnswer
    from founder.observability.tracer import Trace


def serialize_evidence(evidence: "Evidence") -> dict:
    """Serialize Evidence to JSON-safe dict."""

    return {
        "evidence_id": evidence.evidence_id,
        "source": evidence.source,
        "document_type": evidence.document_type,
        "text": evidence.text,
        "score": float(evidence.score) if evidence.score else None,
        "ticker": evidence.ticker,
        "section": evidence.section,
        "published_at": evidence.published_at,
        "metadata": evidence.metadata or {},
    }


def serialize_answer(answer: "GeneratedAnswer") -> dict:
    """Serialize GeneratedAnswer to JSON-safe dict."""

    return {
        "text": answer.answer,
        "claims": [
            {
                "text": claim.text,
                "evidence_ids": claim.evidence_ids,
                "claim_type": claim.claim_type,
                "confidence": float(claim.confidence),
            }
            for claim in answer.claims
        ],
        "citations": [
            {
                "citation_id": citation.citation_id,
                "evidence_id": citation.evidence_id,
                "citation_text": citation.citation_text,
                "source": citation.source,
                "date": citation.date,
            }
            for citation in answer.citations
        ],
        "limitations": answer.limitations or [],
    }


def serialize_trace(trace: "Trace") -> dict:
    """Serialize Trace to JSON-safe dict."""

    return trace.to_dict()


def serialize_full_response(
    query: str,
    trace_id: str,
    answer: "GeneratedAnswer",
    evidence: list["Evidence"],
    trace: Optional["Trace"] = None,
) -> str:
    """Serialize complete response (answer + evidence + trace) to JSON."""

    response = {
        "trace_id": trace_id,
        "query": query,
        "answer": serialize_answer(answer),
        "evidence": [serialize_evidence(e) for e in evidence],
    }

    if trace:
        response["trace"] = serialize_trace(trace)

    return json.dumps(response, default=str, indent=2)
