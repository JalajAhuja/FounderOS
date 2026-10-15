"""Contradiction detection (Step 16).

Pipeline: retrieved evidence -> claim extraction (`reasoning.claims`) ->
grouping by (ticker, section) -> pairwise polarity comparison ->
contradiction report.

Important distinction preserved: a claim pair with opposite polarity in
*different* periods is classified `change_over_time`, not a contradiction
-- e.g. "growth was 20%" (Q2) vs "growth was 12%" (Q4) is a change, not an
incompatible pair of claims about the same point in time.
"""

from itertools import combinations

from founder.reasoning.claims import Claim, extract_all_claims
from founder.reasoning.dates import parse_date, quarter_from_month
from founder.retrieval.evidence import Evidence

POSITIVE_WORDS = {
    "accelerating",
    "accelerate",
    "strong",
    "strength",
    "increase",
    "increasing",
    "robust",
    "record",
    "expand",
    "expanding",
    "momentum",
    "improved",
    "improving",
}

NEGATIVE_WORDS = {
    "decelerating",
    "decline",
    "declining",
    "decrease",
    "decreasing",
    "weak",
    "weakness",
    "slowdown",
    "uncertain",
    "uncertainty",
    "risk",
    "pressure",
    "headwind",
    "challenging",
    "softening",
}


def _polarity(text: str) -> str | None:

    normalized = text.lower()

    has_positive = any(word in normalized for word in POSITIVE_WORDS)
    has_negative = any(word in normalized for word in NEGATIVE_WORDS)

    if has_positive and not has_negative:
        return "positive"

    if has_negative and not has_positive:
        return "negative"

    return None


def _coarse_period(claim: Claim) -> str | None:

    parsed = parse_date(claim.published_at)

    if not parsed:
        return None

    return f"{parsed.year}-Q{quarter_from_month(parsed.month)}"


def _time_relation(period_a: str | None, period_b: str | None) -> str:

    if not period_a or not period_b:
        return "unknown"

    if period_a == period_b:
        return "same"

    return "later" if period_b > period_a else "earlier"


def detect_contradictions(
    evidence_list: list[Evidence],
) -> list[dict]:

    claims = extract_all_claims(evidence_list)

    groups: dict[tuple, list[Claim]] = {}

    for claim in claims:

        key = (claim.ticker, claim.section)

        groups.setdefault(key, []).append(claim)

    report = []

    for claims_in_group in groups.values():

        if len(claims_in_group) < 2:
            continue

        for claim_a, claim_b in combinations(claims_in_group, 2):

            if claim_a.evidence_id == claim_b.evidence_id:
                continue

            polarity_a = _polarity(claim_a.text)
            polarity_b = _polarity(claim_b.text)

            if not polarity_a or not polarity_b:
                continue

            if polarity_a == polarity_b:
                continue

            period_a = _coarse_period(claim_a)
            period_b = _coarse_period(claim_b)

            time_relation = _time_relation(period_a, period_b)

            if time_relation in ("earlier", "later"):

                conflict_type = "change_over_time"
                severity = "low"

            elif claim_a.source != claim_b.source:

                conflict_type = "direct_conflict"
                severity = "medium"

            else:

                conflict_type = "apparent_conflict"
                severity = "low"

            report.append(
                {
                    "claim_a": claim_a.text,
                    "claim_b": claim_b.text,
                    "type": conflict_type,
                    "evidence_a": [claim_a.evidence_id],
                    "evidence_b": [claim_b.evidence_id],
                    "time_relation": time_relation,
                    "severity": severity,
                }
            )

    return report
