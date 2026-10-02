from founder.agent.graph import build_graph


def test_graph_compiles_with_expected_nodes():

    app = build_graph()

    node_names = set(app.get_graph().nodes.keys())

    expected = {
        "analyze_query",
        "plan_retrieval",
        "qdrant_search",
        "graph_search",
        "xbrl_search",
        "news_search",
        "normalize_evidence",
        "grade_evidence",
        "corrective_retrieval",
        "temporal_reasoning",
        "contradiction_check",
        "synthesize",
    }

    assert expected.issubset(node_names)
