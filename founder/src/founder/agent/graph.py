"""Builds and compiles the FounderOS LangGraph agent."""

from langgraph.graph import END, START, StateGraph

from founder.agent import nodes
from founder.agent.routing import route_after_grading
from founder.agent.state import FounderState


def build_graph():

    graph = StateGraph(FounderState)

    graph.add_node("analyze_query", nodes.analyze_query_node)
    graph.add_node("plan_retrieval", nodes.plan_retrieval_node)
    graph.add_node("qdrant_search", nodes.qdrant_search_node)
    graph.add_node("graph_search", nodes.graph_search_node)
    graph.add_node("xbrl_search", nodes.xbrl_search_node)
    graph.add_node("news_search", nodes.news_search_node)
    graph.add_node("normalize_evidence", nodes.normalize_evidence_node)
    graph.add_node("grade_evidence", nodes.grade_evidence_node)
    graph.add_node(
        "corrective_retrieval", nodes.corrective_retrieval_node
    )
    graph.add_node("temporal_reasoning", nodes.temporal_reasoning_node)
    graph.add_node(
        "contradiction_check", nodes.contradiction_check_node
    )
    graph.add_node("synthesize", nodes.synthesize_node)

    graph.add_edge(START, "analyze_query")
    graph.add_edge("analyze_query", "plan_retrieval")

    # Fan-out: each search node independently decides whether to run
    # based on query_plan["sources"].
    graph.add_edge("plan_retrieval", "qdrant_search")
    graph.add_edge("plan_retrieval", "graph_search")
    graph.add_edge("plan_retrieval", "xbrl_search")
    graph.add_edge("plan_retrieval", "news_search")

    # Fan-in.
    graph.add_edge("qdrant_search", "normalize_evidence")
    graph.add_edge("graph_search", "normalize_evidence")
    graph.add_edge("xbrl_search", "normalize_evidence")
    graph.add_edge("news_search", "normalize_evidence")

    graph.add_edge("normalize_evidence", "grade_evidence")

    graph.add_conditional_edges(
        "grade_evidence",
        route_after_grading,
        {
            "corrective_retrieval": "corrective_retrieval",
            "temporal_reasoning": "temporal_reasoning",
        },
    )

    graph.add_edge("corrective_retrieval", "grade_evidence")

    graph.add_edge("temporal_reasoning", "contradiction_check")
    graph.add_edge("contradiction_check", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


_app = None


def get_app():

    global _app

    if _app is None:
        _app = build_graph()

    return _app
