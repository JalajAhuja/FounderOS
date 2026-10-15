"""Manual retrieval evaluation for the Step 14 reranking layer.

Run with:

    python -m founder.evaluation.evaluate_retrieval

Known limitation: `data/05_evaluation/retrieval_questions.json` does not
(yet) carry relevance-labeled evidence/chunk IDs, so true Recall@k/MRR@k
against a ground-truth relevant set cannot be computed here. This script
instead reports a proxy metric -- ticker/source match rate among the
top-k results -- comparing reranking on vs. off. A fuller evaluation
harness with real relevance judgements is Step 20's job.
"""

import json
from pathlib import Path

from founder.retrieval.evidence import qdrant_to_evidence
from founder.retrieval.hybrid_search import HybridRetriever
from founder.retrieval.reranker import FINAL_TOP_K, RERANK_CANDIDATES, Reranker

QUESTIONS_FILE = Path("data/05_evaluation/retrieval_questions.json")


def _match_rate(evidence, expected_tickers, expected_sources):

    if not evidence:
        return 0.0

    hits = 0

    for item in evidence:

        ticker_ok = (
            not expected_tickers
            or item.ticker in expected_tickers
        )

        source_ok = (
            not expected_sources
            or (item.document_type or "").lower() in [
                source.lower() for source in expected_sources
            ]
            or item.source.lower() in [
                source.lower() for source in expected_sources
            ]
        )

        if ticker_ok and source_ok:
            hits += 1

    return hits / len(evidence)


def evaluate(reranker_enabled: bool):

    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    retriever = HybridRetriever()
    reranker = Reranker(enabled=reranker_enabled)

    rates = []

    for question in questions:

        points = retriever.search(
            question["question"],
            top_k=RERANK_CANDIDATES,
        )

        evidence = [qdrant_to_evidence(point) for point in points]

        evidence = reranker.rerank(
            question["question"], evidence, top_k=FINAL_TOP_K
        )

        rate = _match_rate(
            evidence,
            question.get("expected_tickers", []),
            question.get("expected_sources", []),
        )

        rates.append(rate)

        print(f"{question['id']}: match_rate@{FINAL_TOP_K} = {rate:.2f}")

    average = sum(rates) / len(rates) if rates else 0.0

    print(
        f"\nAverage match_rate@{FINAL_TOP_K} "
        f"(reranker_enabled={reranker_enabled}): {average:.3f}"
    )

    return average


def main():

    print("== Without reranking ==")
    without = evaluate(reranker_enabled=False)

    print("\n== With reranking ==")
    with_rerank = evaluate(reranker_enabled=True)

    print(
        f"\nDelta: {with_rerank - without:+.3f} "
        f"(positive means reranking improved the proxy metric)"
    )


if __name__ == "__main__":
    main()
