"""Qdrant hybrid (dense + sparse) semantic retrieval tool."""

import time

from founder.agent.tools.base import ToolResult, get_bundle
from founder.retrieval.evidence import qdrant_to_evidence
from founder.retrieval.reranker import RERANK_CANDIDATES, Reranker


_reranker = Reranker()


def search_qdrant(
    query: str,
    ticker: str | None,
    top_k: int,
) -> ToolResult:

    start = time.perf_counter()

    bundle = get_bundle()

    # Retrieve a broader candidate set than `top_k`, then rerank down to
    # `top_k` -- never rerank the whole corpus.
    points = bundle.vector.search(
        query=query,
        top_k=max(top_k, RERANK_CANDIDATES),
        ticker=ticker,
    )

    evidence = [
        qdrant_to_evidence(point)
        for point in points
    ]

    evidence = _reranker.rerank(
        query,
        evidence,
        top_k=top_k,
    )

    latency_ms = (time.perf_counter() - start) * 1000

    return ToolResult(
        success=True,
        evidence=evidence,
        metadata={"count": len(evidence)},
        latency_ms=latency_ms,
    )
