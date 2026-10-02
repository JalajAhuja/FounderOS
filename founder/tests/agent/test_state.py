from founder.agent.state import FounderState, initial_state


def test_initial_state_defaults():

    state = initial_state("What was MSFT revenue?")

    assert state["query"] == "What was MSFT revenue?"
    assert state["evidence"] == []
    assert state["retrieval_runs"] == []
    assert state["errors"] == []
    assert state["answer"] is None


def test_state_reducer_merges_lists():
    """The `evidence`/`errors` fields use operator.add so fan-out nodes can
    each append independently. Simulate what LangGraph does when merging
    two partial updates for the same key.
    """

    import operator

    state: FounderState = initial_state("q")

    update_a = {"evidence": [1, 2]}
    update_b = {"evidence": [3]}

    merged = operator.add(
        state["evidence"] + update_a["evidence"],
        update_b["evidence"],
    )

    assert merged == [1, 2, 3]
