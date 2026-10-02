"""External news article retrieval tool."""

import time

from founder.agent.tools.base import ToolResult, get_bundle
from founder.retrieval.evidence import news_to_evidence


def search_news(
    query: str,
    ticker: str | None,
    top_k: int,
) -> ToolResult:

    start = time.perf_counter()

    bundle = get_bundle()

    articles = bundle.news.search(
        query=query,
        ticker=ticker,
        top_k=top_k,
    )

    evidence = [
        news_to_evidence(article, index)
        for index, article in enumerate(articles)
    ]

    latency_ms = (time.perf_counter() - start) * 1000

    return ToolResult(
        success=True,
        evidence=evidence,
        metadata={"count": len(evidence)},
        latency_ms=latency_ms,
    )
