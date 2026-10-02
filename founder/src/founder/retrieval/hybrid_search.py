from qdrant_client import (
    QdrantClient,
    models,
)

from fastembed import (
    SparseTextEmbedding,
    TextEmbedding,
)

from founder.retrieval.config import (
    QDRANT_URL,
    COLLECTION_NAME,
    DENSE_MODEL_NAME,
    SPARSE_MODEL_NAME,
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
    PREFETCH_LIMIT,
    DEFAULT_TOP_K,
)


class HybridRetriever:

    def __init__(self):

        # ----------------------------------------------------
        # Qdrant
        # ----------------------------------------------------

        self.client = QdrantClient(
            url=QDRANT_URL
        )

        # ----------------------------------------------------
        # Dense model
        # ----------------------------------------------------

        self.dense_model = TextEmbedding(
            model_name=DENSE_MODEL_NAME
        )

        # ----------------------------------------------------
        # Sparse model
        # ----------------------------------------------------

        self.sparse_model = SparseTextEmbedding(
            model_name=SPARSE_MODEL_NAME
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        ticker: str | None = None,
        source: str | None = None,
        document_type: str | None = None,
    ):

        query = query.strip()

        if not query:

            raise ValueError(
                "Query cannot be empty."
            )

        # ----------------------------------------------------
        # Dense query embedding
        # ----------------------------------------------------

        dense_vector = next(
            self.dense_model.query_embed(
                [query]
            )
        )

        # ----------------------------------------------------
        # Sparse query embedding
        # ----------------------------------------------------

        sparse_vector = next(
            self.sparse_model.query_embed(
                [query]
            )
        )

        # ----------------------------------------------------
        # Build optional filters
        # ----------------------------------------------------

        conditions = []

        if ticker:

            conditions.append(
                models.FieldCondition(
                    key="ticker",
                    match=models.MatchValue(
                        value=ticker.upper()
                    ),
                )
            )

        if source:

            conditions.append(
                models.FieldCondition(
                    key="source",
                    match=models.MatchValue(
                        value=source
                    ),
                )
            )

        if document_type:

            conditions.append(
                models.FieldCondition(
                    key="document_type",
                    match=models.MatchValue(
                        value=document_type
                    ),
                )
            )

        query_filter = None

        if conditions:

            query_filter = models.Filter(
                must=conditions
            )

        # ----------------------------------------------------
        # Hybrid query
        # ----------------------------------------------------

        results = self.client.query_points(

            collection_name=COLLECTION_NAME,

            prefetch=[

                # Dense semantic retrieval
                models.Prefetch(
                    query=dense_vector.tolist(),
                    using=DENSE_VECTOR_NAME,
                    limit=PREFETCH_LIMIT,
                ),

                # Sparse lexical retrieval
                models.Prefetch(
                    query=models.SparseVector(
                        indices=(
                            sparse_vector
                            .indices
                            .tolist()
                        ),
                        values=(
                            sparse_vector
                            .values
                            .tolist()
                        ),
                    ),
                    using=SPARSE_VECTOR_NAME,
                    limit=PREFETCH_LIMIT,
                ),
            ],

            # Reciprocal Rank Fusion
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),

            query_filter=query_filter,

            limit=top_k,

            with_payload=True,
        )

        return results.points


# ============================================================
# CLI TEST
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("FounderOS - Hybrid Retrieval Test")
    print("=" * 70)

    retriever = HybridRetriever()

    query = input(
        "\nEnter query: "
    ).strip()

    results = retriever.search(
        query,
        top_k=8,
    )

    print(
        f"\nRetrieved {len(results)} results."
    )

    print("\n" + "-" * 70)

    for rank, point in enumerate(
        results,
        start=1,
    ):

        payload = point.payload or {}

        print(
            f"\n#{rank}"
        )

        print(
            f"Score: {point.score}"
        )

        print(
            f"Ticker: "
            f"{payload.get('ticker')}"
        )

        print(
            f"Source: "
            f"{payload.get('source')}"
        )

        print(
            f"Document: "
            f"{payload.get('document_type')}"
        )

        print(
            f"Section: "
            f"{payload.get('section')}"
        )

        print(
            f"Date: "
            f"{payload.get('published_at')}"
        )

        text = payload.get(
            "text",
            ""
        )

        preview = text[:800]

        print(
            f"\n{preview}"
        )

        if len(text) > 800:
            print("...")


if __name__ == "__main__":
    main()