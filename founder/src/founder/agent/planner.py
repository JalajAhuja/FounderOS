"""Deterministic retrieval planner.

Converts the raw query-analysis signals from
`founder.retrieval.query_analyzer.analyze_query` into an explicit,
executable retrieval plan: an intent label plus the concrete set of tools
to run, before any retrieval happens.
"""

from founder.retrieval.query_analyzer import analyze_query, normalize

INTENT_TEMPORAL = "temporal"
INTENT_RELATIONSHIP = "relationship"
INTENT_FACTUAL = "factual"
INTENT_STRATEGIC = "strategic"
INTENT_SEMANTIC = "semantic"


EXTERNAL_EVENT_KEYWORDS = [
    "news",
    "announce",
    "announcement",
    "event",
    "regulatory",
    "regulation",
    "lawsuit",
    "press release",
    "market reaction",
    "external",
]


# Sources selected per intent. "timeline" is not a search node itself; it
# tells `temporal_reasoning` to build a period-grouped timeline from the
# evidence gathered by qdrant/graph.
INTENT_SOURCES = {
    INTENT_TEMPORAL: ["graph", "qdrant", "timeline"],
    INTENT_RELATIONSHIP: ["graph"],
    INTENT_FACTUAL: ["facts"],
    INTENT_STRATEGIC: ["facts", "graph", "qdrant"],
    INTENT_SEMANTIC: ["qdrant"],
}


def classify_intent(flags: dict) -> str:
    """Deterministic priority order.

    Temporal and relationship signals are the most specific and take
    priority over the broader factual/strategic/semantic buckets, so a
    query like "What changed in Microsoft's AI strategy between Q2 2025
    and Q1 2026?" is classified as temporal rather than strategic.
    """

    if flags.get("is_temporal"):
        return INTENT_TEMPORAL

    if flags.get("is_graph"):
        return INTENT_RELATIONSHIP

    if flags.get("is_fact"):
        return INTENT_FACTUAL

    if flags.get("is_strategic"):
        return INTENT_STRATEGIC

    return INTENT_SEMANTIC


def needs_external_events(query: str) -> bool:

    normalized = normalize(query)

    return any(
        keyword in normalized
        for keyword in EXTERNAL_EVENT_KEYWORDS
    )


def build_retrieval_plan(
    query: str,
    known_tickers=None,
) -> dict:
    """Build the explicit, deterministic retrieval plan for `query`.

    Returns a dict consumed by the agent graph's search nodes (`sources`,
    `ticker`) as well as richer planning metadata (`intent`,
    `needs_temporal_comparison`, `needs_external_events`).
    """

    flags = analyze_query(
        query,
        known_tickers=known_tickers,
    )

    intent = classify_intent(flags)

    sources = set(INTENT_SOURCES[intent])

    external_events = needs_external_events(query)

    if external_events:
        sources.add("news")

    return {
        "query": query,
        "ticker": flags["ticker"],
        "intent": intent,
        "sources": sorted(sources),
        "needs_temporal_comparison": flags["is_temporal"],
        "needs_external_events": external_events,
        "is_fact": flags["is_fact"],
        "is_graph": flags["is_graph"],
        "is_temporal": flags["is_temporal"],
        "is_strategic": flags["is_strategic"],
    }
