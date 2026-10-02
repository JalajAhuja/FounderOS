"""Evidence sufficiency grading (Step 17).

Evaluates coverage, source diversity, temporal coverage, entity coverage,
and directness against the query plan's needs, and reports what is
missing so `corrective.py` can choose a targeted broadening strategy.
"""

from founder.reasoning.dates import normalize_period
from founder.retrieval.evidence import Evidence


def assess_sufficiency(
    query_plan: dict,
    evidence: list[Evidence],
    contradictions: list[dict] | None = None,
) -> dict:

    contradictions = contradictions or []

    coverage = len(evidence)

    source_diversity = len({item.source for item in evidence})

    periods = {
        normalize_period(item)["period"]
        for item in evidence
    }

    periods.discard("unknown")

    temporal_coverage = len(periods)

    entity_coverage = len(
        {item.ticker for item in evidence if item.ticker}
    )

    ticker = query_plan.get("ticker")

    directness = (
        sum(1 for item in evidence if item.ticker == ticker) / coverage
        if ticker and coverage
        else 1.0
    )

    reasons = []
    missing = []
    sufficient = True

    if coverage == 0:

        sufficient = False
        reasons.append("No evidence retrieved.")
        missing.append("any_evidence")

    if query_plan.get("needs_temporal_comparison") and temporal_coverage < 2:

        sufficient = False
        reasons.append("Only one reporting period found.")
        missing.append("prior_period")

    if query_plan.get(
        "needs_external_events"
    ) and not any(item.source == "News" for item in evidence):

        sufficient = False
        reasons.append("Question asks for an external cause but no news evidence was found.")
        missing.append("external_event")

    if query_plan.get("is_fact") and not any(
        item.document_type == "financial_fact" for item in evidence
    ):

        sufficient = False
        reasons.append("No supporting financial-fact (XBRL) evidence.")
        missing.append("financial_fact")

    return {
        "sufficient": sufficient,
        "reason": reasons,
        "missing": missing,
        "evidence_count": coverage,
        "source_diversity": source_diversity,
        "temporal_coverage": temporal_coverage,
        "entity_coverage": entity_coverage,
        "directness": round(directness, 3),
        "contradiction_count": len(contradictions),
    }
