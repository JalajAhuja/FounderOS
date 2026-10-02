"""Low-level comparison helpers used by `reasoning.temporal.detect_change`.

Never claims causality from ordering alone -- these helpers only report
observed differences between two evidence groups.
"""

from founder.retrieval.evidence import Evidence


def compare_fact_values(
    evidence_a: list[Evidence],
    evidence_b: list[Evidence],
) -> list[dict]:
    """Compare XBRL fact evidence grouped by concept (`section`)."""

    def by_concept(evidence_list):

        grouped = {}

        for item in evidence_list:

            if item.document_type != "financial_fact":
                continue

            grouped.setdefault(item.section, []).append(item)

        return grouped

    facts_a = by_concept(evidence_a)
    facts_b = by_concept(evidence_b)

    changes = []

    for concept in sorted(set(facts_a) & set(facts_b)):

        value_a = facts_a[concept][0].metadata.get("value")
        value_b = facts_b[concept][0].metadata.get("value")

        if value_a == value_b:
            continue

        changes.append(
            {
                "dimension": concept,
                "before": value_a,
                "after": value_b,
                "evidence_ids": [
                    facts_a[concept][0].evidence_id,
                    facts_b[concept][0].evidence_id,
                ],
            }
        )

    return changes


def compare_text_snippets(
    evidence_a: list[Evidence],
    evidence_b: list[Evidence],
) -> list[dict]:
    """Compare narrative (Qdrant/News/Graph) evidence.

    This is a coverage-level comparison, not semantic diffing: it
    surfaces the highest-scoring statement from each period as the
    "before"/"after" narrative so a human (or the synthesis step) can
    judge what changed. It does not itself decide what changed.
    """

    def narrative_only(evidence_list):

        return [
            item
            for item in evidence_list
            if item.document_type != "financial_fact"
        ]

    narrative_a = narrative_only(evidence_a)
    narrative_b = narrative_only(evidence_b)

    if not narrative_a or not narrative_b:
        return []

    top_a = max(narrative_a, key=lambda item: item.score)
    top_b = max(narrative_b, key=lambda item: item.score)

    if top_a.text.strip() == top_b.text.strip():
        return []

    return [
        {
            "dimension": "narrative",
            "before": top_a.text,
            "after": top_b.text,
            "evidence_ids": [
                top_a.evidence_id,
                top_b.evidence_id,
            ],
        }
    ]
