import pytest

from founder.workflows import run_workflow, workflow_request


def test_founder_workflow_commands_are_explicit():
    request = workflow_request("/compare", "msft", "crm")
    assert request.name == "competitive_comparison"
    assert request.tickers == ("MSFT", "CRM")
    assert "AI strategy" in request.query


def test_unknown_workflow_has_actionable_error():
    with pytest.raises(ValueError, match="Expected"):
        workflow_request("/unknown", "MSFT")


def test_runner_adds_workflow_metadata():
    result = run_workflow("/brief", "MSFT", runner=lambda query: {"answer": query})
    assert result["workflow"] == "strategy_brief"
    assert result["answer"].startswith("Prepare a source-backed")