"""Conditional-edge routing functions for the LangGraph agent."""

from founder.agent.config import MAX_RETRIEVAL_ROUNDS
from founder.agent.state import FounderState


def route_after_grading(state: FounderState) -> str:

    sufficiency = state.get("sufficiency") or {}

    if sufficiency.get("sufficient"):
        return "temporal_reasoning"

    if sufficiency.get("rounds", 0) >= MAX_RETRIEVAL_ROUNDS:
        return "temporal_reasoning"

    return "corrective_retrieval"
