import operator
from typing import Annotated, Any, TypedDict

from founder.retrieval.evidence import Evidence


class FounderState(TypedDict):
    """Typed state threaded through the LangGraph agent.

    `evidence`, `retrieval_runs`, and `errors` use an additive reducer
    (`operator.add`) so parallel search nodes and the corrective retry can
    each append independently without clobbering each other's updates.
    """

    query: str

    query_plan: dict[str, Any]

    evidence: Annotated[list[Evidence], operator.add]

    retrieval_runs: Annotated[list[dict[str, Any]], operator.add]

    temporal_context: dict[str, Any]

    contradictions: list[dict[str, Any]]

    sufficiency: dict[str, Any]

    answer: str | None

    claims: list[dict[str, Any]]

    citations: list[dict[str, Any]]

    limitations: list[str]

    errors: Annotated[list[str], operator.add]

    trace_id: str | None


def initial_state(
    query: str,
    trace_id: str | None = None,
) -> FounderState:

    return FounderState(
        query=query,
        query_plan={},
        evidence=[],
        retrieval_runs=[],
        temporal_context={},
        contradictions=[],
        sufficiency={},
        answer=None,
        claims=[],
        citations=[],
        limitations=[],
        errors=[],
        trace_id=trace_id,
    )
