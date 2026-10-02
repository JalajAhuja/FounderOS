"""Unit tests for retrieval evaluation metrics."""

from founder.evaluation.metrics import (
    compute_ndcg,
    compute_mrr,
    compute_recall,
)


def test_ndcg_perfect_ranking():

    retrieved = ["d1", "d2", "d3"]
    relevant = ["d1", "d2", "d3"]

    assert compute_ndcg(retrieved, relevant) == 1.0


def test_ndcg_no_relevant():

    retrieved = ["d1", "d2"]
    relevant = []

    assert compute_ndcg(retrieved, relevant) == 0.0


def test_ndcg_partial():

    retrieved = ["d1", "d3", "d2"]
    relevant = ["d1", "d2"]

    # d1 at rank 1 (relevant), d3 at rank 2 (not), d2 at rank 3 (relevant)
    # DCG = 1/1 + 0/log2(3) + 1/log2(4) = 1 + 0 + 0.5 = 1.5
    # IDCG (perfect: d1, d2, d3) = 1/1 + 1/log2(3) ≈ 1 + 0.631 = 1.631
    # NDCG ≈ 1.5 / 1.631 ≈ 0.92

    ndcg = compute_ndcg(retrieved, relevant)

    assert 0.90 < ndcg < 0.95


def test_ndcg_at_k():

    retrieved = ["d1", "d2", "d3", "d4"]
    relevant = ["d1", "d2"]

    ndcg_at_2 = compute_ndcg(retrieved, relevant, k=2)
    ndcg_at_3 = compute_ndcg(retrieved, relevant, k=3)

    assert ndcg_at_2 == 1.0
    # Both relevant docs already sit at ranks 1-2, the ideal arrangement,
    # so extending the window to k=3 doesn't lower the score.
    assert ndcg_at_3 == 1.0


def test_mrr_first_relevant_at_rank_1():

    retrieved = ["d1", "d2"]
    relevant = ["d1"]

    assert compute_mrr(retrieved, relevant) == 1.0


def test_mrr_first_relevant_at_rank_3():

    retrieved = ["d1", "d2", "d3"]
    relevant = ["d3"]

    assert compute_mrr(retrieved, relevant) == 1.0 / 3


def test_mrr_no_relevant():

    retrieved = ["d1", "d2"]
    relevant = ["d3"]

    assert compute_mrr(retrieved, relevant) == 0.0


def test_recall_all_found():

    retrieved = ["d1", "d2", "d3"]
    relevant = ["d1", "d2"]

    assert compute_recall(retrieved, relevant) == 1.0


def test_recall_partial():

    retrieved = ["d1", "d2", "d3"]
    relevant = ["d1", "d2", "d4"]

    assert compute_recall(retrieved, relevant) == 2 / 3


def test_recall_at_k():

    retrieved = ["d1", "d2", "d3", "d4"]
    relevant = ["d1", "d2", "d3"]

    recall_at_2 = compute_recall(retrieved, relevant, k=2)
    recall_at_3 = compute_recall(retrieved, relevant, k=3)
    recall_at_4 = compute_recall(retrieved, relevant, k=4)

    assert recall_at_2 == 2 / 3
    assert recall_at_3 == 1.0
    assert recall_at_4 == 1.0
