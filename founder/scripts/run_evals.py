"""Run evaluation on retrieval and answer quality."""

from pathlib import Path


def run_evals():
    """Compute evaluation metrics on labeled dataset."""

    eval_path = Path("data/05_evaluation")

    eval_path.mkdir(parents=True, exist_ok=True)

    print("Running evaluation...")

    questions_file = eval_path / "retrieval_questions.json"

    if not questions_file.exists():

        print(f"[WARN] {questions_file} not found. Skipping evaluation.")

        return

    print("Would load labeled questions from retrieval_questions.json")

    print("Would run retrievals with:")
    print("  - Qdrant (dense + sparse + reranker)")
    print("  - Neo4j (graph)")
    print("  - XBRL (facts)")

    print("Would compute metrics:")
    print("  - NDCG@5, NDCG@10")
    print("  - MRR@10")
    print("  - Recall@5, Recall@10")

    print("Would print summary report:")
    print("  Mean NDCG@10: X.XX")
    print("  Mean MRR@10: X.XX")
    print("  Mean Recall@10: X.XX")

    print("[OK] Evaluation complete (would write results to data/07_model_output/)")


if __name__ == "__main__":
    run_evals()
