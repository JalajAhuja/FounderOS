from founder.retrieval.hybrid_search import (
    HybridRetriever,
)

from founder.retrieval.fact_retriever import (
    FactRetriever,
)

from founder.retrieval.graph_retriever import (
    GraphRetriever,
)

from founder.retrieval.query_analyzer import (
    analyze_query,
)

from founder.retrieval.evidence import (
    Evidence,
    fact_to_evidence,
    graph_to_evidence,
    qdrant_to_evidence,
)


class UnifiedRetriever:

    def __init__(self):

        print(
            "\nInitializing FounderOS "
            "Unified Retriever..."
        )

        # ----------------------------------------------------
        # Qdrant
        # ----------------------------------------------------

        self.vector = HybridRetriever()

        # ----------------------------------------------------
        # XBRL
        # ----------------------------------------------------

        self.facts = FactRetriever()

        # ----------------------------------------------------
        # Neo4j
        # ----------------------------------------------------

        self.graph = GraphRetriever()

        # ----------------------------------------------------
        # Known tickers
        # ----------------------------------------------------

        self.known_tickers = (
            self.facts.tickers
        )

        print(
            "Unified Retriever ready."
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query,
        top_k=8,
    ):

        plan = analyze_query(
            query,
            known_tickers=self.known_tickers,
        )

        print(
            "\nRetrieval plan:"
        )

        print(
            f"  ticker: "
            f"{plan['ticker']}"
        )

        print(
            f"  sources: "
            f"{plan['sources']}"
        )

        print(
            f"  fact query: "
            f"{plan['is_fact']}"
        )

        print(
            f"  graph query: "
            f"{plan['is_graph']}"
        )

        print(
            f"  temporal: "
            f"{plan['is_temporal']}"
        )

        print(
            f"  strategic: "
            f"{plan['is_strategic']}"
        )

        evidence = []

        # ====================================================
        # 1. QDRANT
        # ====================================================

        if "qdrant" in plan["sources"]:

            qdrant_results = (
                self.vector.search(
                    query=query,
                    top_k=top_k,
                    ticker=plan["ticker"],
                )
            )

            for point in qdrant_results:

                evidence.append(
                    qdrant_to_evidence(
                        point
                    )
                )

        # ====================================================
        # 2. XBRL
        # ====================================================

        if "facts" in plan["sources"]:

            fact_results = (
                self.facts.search(
                    query=query,
                    ticker=plan["ticker"],
                    top_k=top_k,
                )
            )

            for index, fact in enumerate(
                fact_results
            ):

                evidence.append(
                    fact_to_evidence(
                        fact,
                        index,
                    )
                )

        # ====================================================
        # 3. NEO4J
        # ====================================================

        if "graph" in plan["sources"]:

            graph_results = (
                self.graph.search(
                    query=query,
                    ticker=plan["ticker"],
                    top_k=top_k,
                )
            )

            for index, item in enumerate(
                graph_results
            ):

                evidence.append(
                    graph_to_evidence(
                        item,
                        index,
                    )
                )

        # ====================================================
        # 4. DEDUPLICATION
        # ====================================================

        unique = {}

        for item in evidence:

            if (
                item.evidence_id
                not in unique
            ):

                unique[
                    item.evidence_id
                ] = item

        evidence = list(
            unique.values()
        )

        # ====================================================
        # 5. SORT
        # ====================================================

        evidence.sort(
            key=lambda item: (
                item.score
            ),
            reverse=True,
        )

        return {
            "query": query,
            "plan": plan,
            "evidence": evidence[:top_k],
        }

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        self.graph.close()