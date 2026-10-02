"""Neo4j entity/relationship graph retrieval tool."""

import time

from founder.agent.tools.base import ToolResult, get_bundle
from founder.retrieval.evidence import graph_to_evidence


def search_graph(
    query: str,
    ticker: str | None,
    top_k: int,
) -> ToolResult:

    start = time.perf_counter()

    bundle = get_bundle()

    items = bundle.graph.search(
        query=query,
        ticker=ticker,
        top_k=top_k,
    )

    evidence = [
        graph_to_evidence(item, index)
        for index, item in enumerate(items)
    ]

    latency_ms = (time.perf_counter() - start) * 1000

    return ToolResult(
        success=True,
        evidence=evidence,
        metadata={"count": len(evidence)},
        latency_ms=latency_ms,
    )
