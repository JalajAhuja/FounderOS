"""Retrieval evaluation metrics (NDCG, MRR, Recall)."""

import math
from collections.abc import Sequence


def compute_dcg(relevances: Sequence[float], k: int | None = None) -> float:
    """Discounted cumulative gain: sum(rel_i / log2(i+1))."""

    if k:
        relevances = relevances[:k]

    dcg = 0.0

    for i, rel in enumerate(relevances, start=1):
        dcg += rel / math.log2(i + 1)

    return dcg


def compute_ndcg(
    retrieved_ids: Sequence[str],
    relevant_ids: Sequence[str],
    k: int | None = None,
) -> float:
    """Normalized DCG: DCG / IDCG.

    Assumes binary relevance (relevant_id in set = 1, else 0).
    """

    if not relevant_ids or not retrieved_ids:
        return 0.0

    relevant_set = set(relevant_ids)

    relevances = [
        1.0 if doc_id in relevant_set else 0.0
        for doc_id in retrieved_ids
    ]

    dcg = compute_dcg(relevances, k)

    # IDCG: perfect ranking where all relevant docs come first.
    ideal_relevances = [1.0] * min(len(relevant_ids), len(retrieved_ids))

    if k:
        ideal_relevances = ideal_relevances[:k]

    idcg = compute_dcg(ideal_relevances, k)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def compute_mrr(
    retrieved_ids: Sequence[str],
    relevant_ids: Sequence[str],
    k: int | None = None,
) -> float:
    """Mean reciprocal rank: 1 / (rank of first relevant doc).

    If no relevant doc found, returns 0.
    """

    relevant_set = set(relevant_ids)

    if k:
        retrieved_ids = retrieved_ids[:k]

    for rank, doc_id in enumerate(retrieved_ids, start=1):

        if doc_id in relevant_set:
            return 1.0 / rank

    return 0.0


def compute_recall(
    retrieved_ids: Sequence[str],
    relevant_ids: Sequence[str],
    k: int | None = None,
) -> float:
    """Recall@k: fraction of relevant docs found in top-k."""

    if not relevant_ids:
        return 0.0

    relevant_set = set(relevant_ids)

    if k:
        retrieved_ids = retrieved_ids[:k]

    found = sum(1 for doc_id in retrieved_ids if doc_id in relevant_set)

    return found / len(relevant_ids)
