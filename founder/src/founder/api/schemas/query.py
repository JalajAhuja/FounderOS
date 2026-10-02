"""Query response schemas."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class QueryRequest:
    """Query request."""

    query: str
    top_k: int = 8


@dataclass
class QueryResponse:
    """Query response."""

    trace_id: str
    query: str
    answer: str
    claims: list
    citations: list
    evidence: list
    latency_ms: int
