"""Founder-oriented query workflows built on the existing agent runner."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class WorkflowRequest:
    name: str
    tickers: tuple[str, ...]
    query: str


def workflow_request(command: str, *arguments: str) -> WorkflowRequest:
    """Translate product commands into explicit, auditable questions."""
    command = command.lstrip("/").casefold()
    if command == "company" and arguments:
        ticker = arguments[0].upper()
        return WorkflowRequest("company_brief", (ticker,), f"Prepare a company brief for {ticker}: business, financial trajectory, strategy, competitors, events, commentary, risks, and open questions.")
    if command == "compare" and len(arguments) >= 2:
        tickers = tuple(item.upper() for item in arguments[:2])
        return WorkflowRequest("competitive_comparison", tickers, f"Compare {tickers[0]} and {tickers[1]} across AI strategy, pricing, growth, margins, products, management commentary, and competitive mentions.")
    if command == "changes" and arguments:
        ticker = arguments[0].upper()
        return WorkflowRequest("change_monitor", (ticker,), f"Identify changed guidance, products, partnerships, competitors, claims, and risks for {ticker} across the available periods.")
    if command == "brief" and arguments:
        ticker = arguments[0].upper()
        return WorkflowRequest("strategy_brief", (ticker,), f"Prepare a source-backed investment and strategy brief for {ticker}, including narrative, financial signals, strategic shifts, events, contradictions, and open questions.")
    raise ValueError("Expected /company TICKER, /compare TICKER TICKER, /changes TICKER, or /brief TICKER")


def run_workflow(command: str, *arguments: str, runner: Callable[[str], dict[str, Any]] | None = None) -> dict[str, Any]:
    request = workflow_request(command, *arguments)
    result = runner(request.query) if runner else {"query": request.query, "workflow": request.name, "tickers": request.tickers}
    return {"workflow": request.name, "tickers": list(request.tickers), **result}