"""Temporal grouping helper for evidence already retrieved by other tools.

This is a placeholder over the future provenance-preserving temporal graph
(Step 13) and the full temporal reasoning engine (Step 15). It does not run
its own retrieval — it composes evidence already gathered by the vector and
graph tools into a period-ordered timeline.
"""

from collections import defaultdict

from founder.retrieval.evidence import Evidence


def build_timeline(
    evidence: list[Evidence],
) -> dict:

    periods = defaultdict(list)

    for item in evidence:

        published_at = item.published_at

        period = str(published_at)[:4] if published_at else "unknown"

        periods[period].append(item.evidence_id)

    ordered_periods = sorted(
        periods.keys(),
        reverse=True,
    )

    return {
        "periods_observed": {
            period: len(periods[period])
            for period in ordered_periods
        },
        "distinct_periods": len(periods),
        "evidence_by_period": dict(periods),
    }
