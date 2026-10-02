"""Temporal reasoning engine (Step 15).

Groups evidence by fiscal/publication period and compares two periods,
producing a structured before/after change summary. Never compares
unsorted dates and never infers causality from temporal ordering alone.
"""

from collections import defaultdict

from founder.reasoning.comparisons import (
    compare_fact_values,
    compare_text_snippets,
)
from founder.reasoning.dates import normalize_period
from founder.retrieval.evidence import Evidence


def group_by_period(
    evidence_list: list[Evidence],
) -> dict[str, list[Evidence]]:

    groups = defaultdict(list)

    for item in evidence_list:

        period_info = normalize_period(item)

        groups[period_info["period"]].append(item)

    # Sort periods chronologically ("unknown" last) rather than relying
    # on insertion/dict order.
    def sort_key(period):

        if period == "unknown":
            return (1, "")

        return (0, period)

    return dict(
        sorted(groups.items(), key=lambda pair: sort_key(pair[0]))
    )


def detect_change(
    evidence_a: list[Evidence],
    evidence_b: list[Evidence],
) -> list[dict]:

    changes = compare_fact_values(evidence_a, evidence_b)

    changes.extend(
        compare_text_snippets(evidence_a, evidence_b)
    )

    return changes


def build_change_summary(
    topic: str,
    period_a: str,
    period_b: str,
    changes: list[dict],
) -> dict:

    return {
        "topic": topic,
        "period_a": period_a,
        "period_b": period_b,
        "changes": changes,
    }


def _infer_topic(
    evidence_a: list[Evidence],
    evidence_b: list[Evidence],
) -> str:

    sections = [
        item.section
        for item in (evidence_a + evidence_b)
        if item.section
    ]

    if not sections:
        return "unspecified"

    return max(set(sections), key=sections.count)


def compare_periods(
    evidence_list: list[Evidence],
    period_a: str,
    period_b: str,
    topic: str | None = None,
) -> dict:
    """Compare evidence already grouped into `period_a` and `period_b`
    (period labels as produced by `normalize_period`/`group_by_period`).
    """

    groups = group_by_period(evidence_list)

    evidence_a = groups.get(period_a, [])
    evidence_b = groups.get(period_b, [])

    changes = detect_change(evidence_a, evidence_b)

    resolved_topic = topic or _infer_topic(evidence_a, evidence_b)

    return build_change_summary(
        resolved_topic,
        period_a,
        period_b,
        changes,
    )
