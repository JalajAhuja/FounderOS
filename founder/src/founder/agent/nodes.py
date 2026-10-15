"""LangGraph node implementations.

Each node takes a `FounderState` and returns a partial state update dict.
Nodes call into `agent.tools` for retrieval and never talk to
Qdrant/Neo4j/facts directly.
"""

import time

from founder.agent import tools
from founder.agent.config import DEFAULT_TOP_K
from founder.agent.corrective import build_corrective_plan
from founder.agent.planner import build_retrieval_plan
from founder.agent.state import FounderState
from founder.agent.sufficiency import assess_sufficiency
from founder.agent.tools.timeline_tool import build_timeline
from founder.generation.answer import generate_answer
from founder.reasoning.contradictions import detect_contradictions
from founder.reasoning.temporal import compare_periods, group_by_period
from founder.retrieval.query_analyzer import analyze_query

# ============================================================
# QUERY ANALYSIS / PLANNING
# ============================================================

def analyze_query_node(state: FounderState) -> dict:

    try:

        bundle = tools.get_bundle()

        known_tickers = bundle.known_tickers

    except Exception as error:

        return {
            "errors": [
                f"analyze_query: {error}"
            ],
        }

    plan = analyze_query(
        state["query"],
        known_tickers=known_tickers,
    )

    return {"query_plan": plan}


def plan_retrieval_node(state: FounderState) -> dict:

    try:

        known_tickers = tools.get_bundle().known_tickers

    except Exception as error:

        return {
            "errors": [
                f"plan_retrieval: {error}"
            ],
        }

    # Supersedes analyze_query_node's raw flags with the deterministic,
    # intent-driven executable plan (Step 12).
    plan = build_retrieval_plan(
        state["query"],
        known_tickers=known_tickers,
    )

    return {"query_plan": plan}


# ============================================================
# SEARCH NODES (fan-out)
# ============================================================

def _run_search(
    state: FounderState,
    node_name: str,
    source_key: str,
    search_fn,
) -> dict:

    plan = state.get("query_plan") or {}

    if source_key not in plan.get("sources", []):

        return {
            "retrieval_runs": [
                {
                    "node": node_name,
                    "count": 0,
                    "skipped": True,
                }
            ],
        }

    start = time.perf_counter()

    try:

        result = search_fn(
            query=state["query"],
            ticker=plan.get("ticker"),
            top_k=DEFAULT_TOP_K,
        )

    except Exception as error:

        return {
            "errors": [
                f"{node_name}: {error}"
            ],
            "retrieval_runs": [
                {
                    "node": node_name,
                    "count": 0,
                    "error": str(error),
                }
            ],
        }

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    return {
        "evidence": result.evidence,
        "retrieval_runs": [
            {
                "node": node_name,
                "count": len(result.evidence),
                "latency_ms": latency_ms,
            }
        ],
    }


def qdrant_search_node(state: FounderState) -> dict:

    return _run_search(
        state,
        "qdrant_search",
        "qdrant",
        tools.search_qdrant,
    )


def graph_search_node(state: FounderState) -> dict:

    return _run_search(
        state,
        "graph_search",
        "graph",
        tools.search_graph,
    )


def xbrl_search_node(state: FounderState) -> dict:

    return _run_search(
        state,
        "xbrl_search",
        "facts",
        tools.search_facts,
    )


def news_search_node(state: FounderState) -> dict:

    return _run_search(
        state,
        "news_search",
        "news",
        tools.search_news,
    )


# ============================================================
# NORMALIZE / GRADE
# ============================================================

def normalize_evidence_node(state: FounderState) -> dict:

    unique = {}

    for item in state.get("evidence", []):

        if item.evidence_id not in unique:
            unique[item.evidence_id] = item

    deduped = list(unique.values())

    deduped.sort(
        key=lambda item: item.score,
        reverse=True,
    )

    return {"evidence": deduped}


def grade_evidence_node(state: FounderState) -> dict:

    evidence = state.get("evidence", [])

    plan = state.get("query_plan") or {}

    sufficiency = assess_sufficiency(
        plan,
        evidence,
        contradictions=state.get("contradictions"),
    )

    # Preserve the round counter across grading passes; only
    # corrective_retrieval_node increments it.
    sufficiency["rounds"] = (state.get("sufficiency") or {}).get(
        "rounds", 0
    )

    return {"sufficiency": sufficiency}


# ============================================================
# CORRECTIVE RETRIEVAL
# ============================================================

def corrective_retrieval_node(state: FounderState) -> dict:

    sufficiency = dict(
        state.get("sufficiency") or {}
    )

    sufficiency["rounds"] = (
        sufficiency.get("rounds", 0) + 1
    )

    plan = state.get("query_plan") or {}

    correction = build_corrective_plan(
        plan,
        sufficiency.get("missing", []),
        state["query"],
    )

    new_plan = correction["plan"]
    query = correction["query"]

    evidence_updates: list = []
    run_updates: list = []
    error_updates: list = []

    for node_name, source_key, search_fn in (
        ("qdrant_search", "qdrant", tools.search_qdrant),
        ("graph_search", "graph", tools.search_graph),
        ("xbrl_search", "facts", tools.search_facts),
        ("news_search", "news", tools.search_news),
    ):

        if source_key not in new_plan.get("sources", []):
            continue

        try:

            result = search_fn(
                query=query,
                ticker=new_plan.get("ticker"),
                top_k=DEFAULT_TOP_K,
            )

            evidence_updates.extend(result.evidence)

            run_updates.append(
                {
                    "node": f"corrective:{node_name}",
                    "count": len(result.evidence),
                    "strategies": correction["strategies"],
                }
            )

        except Exception as error:

            error_updates.append(
                f"corrective:{node_name}: {error}"
            )

    return {
        "query_plan": new_plan,
        "sufficiency": sufficiency,
        "evidence": evidence_updates,
        "retrieval_runs": run_updates,
        "errors": error_updates,
    }


# ============================================================
# TEMPORAL REASONING (Step 15)
# ============================================================

def temporal_reasoning_node(state: FounderState) -> dict:

    evidence = state.get("evidence", [])

    context = build_timeline(evidence)

    periods = list(group_by_period(evidence).keys())

    periods = [period for period in periods if period != "unknown"]

    if state.get("query_plan", {}).get(
        "needs_temporal_comparison"
    ) and len(periods) >= 2:

        context["comparison"] = compare_periods(
            evidence,
            periods[0],
            periods[-1],
        )

    return {"temporal_context": context}


# ============================================================
# CONTRADICTION CHECK (Step 16)
# ============================================================

def contradiction_check_node(state: FounderState) -> dict:

    contradictions = detect_contradictions(
        state.get("evidence", [])
    )

    return {"contradictions": contradictions}


# ============================================================
# SYNTHESIS (Step 18)
# ============================================================

def synthesize_node(state: FounderState) -> dict:

    evidence = state.get("evidence", [])

    try:

        result = generate_answer(
            query=state["query"],
            evidence=evidence,
            sufficiency=state.get("sufficiency"),
        )

    except Exception as error:

        return {
            "answer": (
                "I couldn't generate an answer due to an internal error: "
                f"{error}"
            ),
            "claims": [],
            "citations": [],
            "limitations": ["Answer generation failed."],
            "errors": [f"synthesize: {error}"],
        }

    return {
        "answer": result.answer,
        "claims": [vars(claim) for claim in result.claims],
        "citations": [vars(citation) for citation in result.citations],
        "limitations": result.limitations,
    }
