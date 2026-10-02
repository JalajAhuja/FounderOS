import re


# ============================================================
# KEYWORD SIGNALS
# ============================================================

FACT_KEYWORDS = [
    "revenue",
    "net income",
    "operating income",
    "gross profit",
    "margin",
    "eps",
    "earnings per share",
    "assets",
    "liabilities",
    "equity",
    "cash",
    "debt",
    "fiscal",
    "fy",
    "q1",
    "q2",
    "q3",
    "q4",
    "how much",
    "how many",
    "what was",
]

GRAPH_KEYWORDS = [
    "compete",
    "competitor",
    "competitors",
    "partner",
    "partnership",
    "acquire",
    "acquisition",
    "acquired",
    "invest",
    "investment",
    "relationship",
    "executive",
    "ceo",
    "cfo",
    "founder",
    "founded",
    "who is",
    "who are",
]

TEMPORAL_KEYWORDS = [
    "change",
    "changed",
    "between",
    "compare",
    "comparison",
    "before",
    "after",
    "quarter over quarter",
    "quarter-over-quarter",
    "year over year",
    "year-over-year",
    "since",
    "trend",
    "over time",
    "latest",
]

STRATEGIC_KEYWORDS = [
    "risk",
    "risks",
    "strategy",
    "strategic",
    "opportunity",
    "opportunities",
    "outlook",
    "implication",
    "implications",
    "should",
    "could",
    "why",
]


# ============================================================
# HELPERS
# ============================================================

def normalize(value):

    return re.sub(
        r"[^a-z0-9 ]+",
        " ",
        str(value).lower(),
    ).strip()


def contains_any(
    normalized_query,
    keywords,
):

    return any(
        keyword in normalized_query
        for keyword in keywords
    )


def infer_ticker(
    query,
    known_tickers=None,
):

    if not known_tickers:
        return None

    query_upper = query.upper()

    for ticker in known_tickers:

        pattern = (
            rf"\b{re.escape(ticker.upper())}\b"
        )

        if re.search(
            pattern,
            query_upper,
        ):
            return ticker.upper()

    return None


# ============================================================
# QUERY ANALYSIS
# ============================================================

def analyze_query(
    query,
    known_tickers=None,
):
    """Classify a natural-language query into a retrieval plan.

    Returns a dict describing which retrieval sources should be
    used and the query's intent flags, consumed by
    UnifiedRetriever.search() and the LangGraph agent planner.
    """

    normalized = normalize(
        query
    )

    ticker = infer_ticker(
        query,
        known_tickers,
    )

    is_fact = contains_any(
        normalized,
        FACT_KEYWORDS,
    )

    is_graph = contains_any(
        normalized,
        GRAPH_KEYWORDS,
    )

    is_temporal = contains_any(
        normalized,
        TEMPORAL_KEYWORDS,
    )

    is_strategic = contains_any(
        normalized,
        STRATEGIC_KEYWORDS,
    )

    sources = set()

    # Strategic questions pull from every available source.
    if is_strategic:

        sources.update(
            {
                "qdrant",
                "graph",
                "facts",
            }
        )

    if is_fact:
        sources.add("facts")

    if is_graph:
        sources.add("graph")

    if is_temporal:

        sources.update(
            {
                "qdrant",
                "graph",
            }
        )

    # Default to semantic search when no other
    # intent has been detected.
    if not sources:
        sources.add("qdrant")

    return {
        "query": query,
        "ticker": ticker,
        "sources": sorted(sources),
        "is_fact": is_fact,
        "is_graph": is_graph,
        "is_temporal": is_temporal,
        "is_strategic": is_strategic,
    }