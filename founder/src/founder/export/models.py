"""Stable investigation export contracts."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InvestigationPack:
    question: str
    answer: str
    claims: list[dict[str, Any]] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    graph_findings: list[dict[str, Any]] = field(default_factory=list)
    financial_facts: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    trace_id: str | None = None
