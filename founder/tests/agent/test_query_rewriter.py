from founder.agent.query_rewriter import broaden_query


def test_broaden_query_strips_year_and_quarter_tokens():

    result = broaden_query(
        "What changed in Microsoft's AI strategy between Q2 2025 and Q1 2026?"
    )

    assert "2025" not in result
    assert "2026" not in result
    assert "Microsoft" in result


def test_broaden_query_returns_original_when_nothing_to_strip():

    query = "What did management say about AI monetization?"

    assert broaden_query(query) == query
