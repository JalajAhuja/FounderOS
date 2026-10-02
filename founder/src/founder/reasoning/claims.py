"""Lightweight claim extraction shared by temporal comparison (Step 15)
and contradiction detection (Step 16).

Deterministic sentence-splitting heuristic, not an LLM call -- keeps this
reusable, fast, and independent of API keys. A future LLM-based extractor
could replace `extract_claims` without changing its return contract.
"""

import re
from dataclasses import dataclass

from founder.retrieval.evidence import Evidence


@dataclass
class Claim:

    text: str

    evidence_id: str

    source: str

    ticker: str | None

    section: str | None

    published_at: str | None


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def extract_claims(
    evidence: Evidence,
    max_claims: int = 5,
) -> list[Claim]:

    text = (evidence.text or "").strip()

    if not text:
        return []

    sentences = [
        sentence.strip()
        for sentence in _SENTENCE_SPLIT.split(text)
        if len(sentence.strip()) >= 20
    ]

    if not sentences:
        sentences = [text]

    return [
        Claim(
            text=sentence,
            evidence_id=evidence.evidence_id,
            source=evidence.source,
            ticker=evidence.ticker,
            section=evidence.section,
            published_at=evidence.published_at,
        )
        for sentence in sentences[:max_claims]
    ]


def extract_all_claims(
    evidence_list: list[Evidence],
) -> list[Claim]:

    claims = []

    for item in evidence_list:
        claims.extend(extract_claims(item))

    return claims
