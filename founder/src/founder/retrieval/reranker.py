"""Cross-encoder reranking over an initial candidate set.

Reranks the top `RERANK_CANDIDATES` results already returned by hybrid
(dense + sparse) retrieval down to `FINAL_TOP_K`. Never reranks the whole
corpus. Falls back to the original ordering (no-op) if disabled or if the
configured model fails to load, so a missing/undownloadable model never
hard-fails retrieval.
"""

import os

from founder.retrieval.evidence import Evidence

RERANKER_ENABLED = (
    os.getenv("RERANKER_ENABLED", "true").lower() == "true"
)

RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "Xenova/ms-marco-MiniLM-L-6-v2",
)

RERANK_CANDIDATES = int(
    os.getenv("RERANK_CANDIDATES", "30")
)

FINAL_TOP_K = int(
    os.getenv("FINAL_TOP_K", "8")
)


class Reranker:

    def __init__(
        self,
        enabled: bool = RERANKER_ENABLED,
        model_name: str = RERANKER_MODEL,
    ):

        self.enabled = enabled
        self.model_name = model_name
        self._model = None

    def _get_model(self):

        if self._model is None:

            from fastembed.rerank.cross_encoder import (
                TextCrossEncoder,
            )

            self._model = TextCrossEncoder(
                model_name=self.model_name
            )

        return self._model

    def rerank(
        self,
        query: str,
        documents: list[Evidence],
        top_k: int = FINAL_TOP_K,
    ) -> list[Evidence]:

        if not self.enabled or not documents:
            return documents[:top_k]

        try:

            model = self._get_model()

            scores = list(
                model.rerank(
                    query,
                    [doc.text for doc in documents],
                )
            )

        except Exception as error:

            print(
                f"WARNING: reranker unavailable ({error}); "
                f"falling back to original order."
            )

            return documents[:top_k]

        ranked = sorted(
            zip(documents, scores),
            key=lambda pair: pair[1],
            reverse=True,
        )

        reranked = []

        for document, score in ranked[:top_k]:

            document.metadata = dict(
                document.metadata or {}
            )

            document.metadata["rerank_score"] = float(score)

            reranked.append(document)

        return reranked
