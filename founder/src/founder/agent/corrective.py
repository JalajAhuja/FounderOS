"""Corrective retrieval strategies (Step 17).

Chooses a targeted broadening strategy from the `missing` signals reported
by `agent.sufficiency.assess_sufficiency`, rather than always broadening
everything.
"""

from founder.agent.query_rewriter import broaden_query


def build_corrective_plan(
    plan: dict,
    missing: list[str],
    query: str,
) -> dict:

    new_plan = dict(plan)

    sources = set(new_plan.get("sources", []))

    strategies = []

    if "any_evidence" in missing:

        new_plan["ticker"] = None
        sources.update({"facts", "graph", "news", "qdrant"})
        strategies.append("ticker_expansion")
        strategies.append("source_expansion")

    if "prior_period" in missing:

        sources.update({"graph", "qdrant", "timeline"})
        strategies.append("period_expansion")

    if "external_event" in missing:

        sources.add("news")
        strategies.append("news_fallback")

    if "financial_fact" in missing:

        sources.add("facts")
        strategies.append("fact_fallback")

    new_plan["sources"] = sorted(sources)

    rewritten_query = (
        broaden_query(query)
        if "any_evidence" in missing
        else query
    )

    if rewritten_query != query:
        strategies.append("query_expansion")

    return {
        "plan": new_plan,
        "query": rewritten_query,
        "strategies": strategies,
    }
