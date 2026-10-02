"""Shared tool primitives: `ToolResult` and the retriever client bundle."""

from dataclasses import dataclass
from typing import Any

from founder.retrieval.evidence import Evidence
from founder.retrieval.fact_retriever import FactRetriever
from founder.retrieval.graph_retriever import GraphRetriever
from founder.retrieval.hybrid_search import HybridRetriever
from founder.retrieval.news_retriever import NewsRetriever


@dataclass
class ToolResult:

    success: bool

    evidence: list[Evidence]

    metadata: dict[str, Any]

    latency_ms: float


class RetrieverBundle:
    """Owns the expensive retriever clients (embeddings, Qdrant, Neo4j).

    Constructed once and reused across agent invocations.
    """

    def __init__(self):

        self.vector = HybridRetriever()

        self.facts = FactRetriever()

        self.graph = GraphRetriever()

        self.news = NewsRetriever()

        self.known_tickers = sorted(
            set(self.facts.tickers) | set(self.news.tickers)
        )

    def close(self):

        self.graph.close()


_bundle: RetrieverBundle | None = None


def get_bundle() -> RetrieverBundle:

    global _bundle

    if _bundle is None:
        _bundle = RetrieverBundle()

    return _bundle
