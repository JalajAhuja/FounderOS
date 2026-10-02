"""Manual evaluation experiment runner (Step 20)."""

from pathlib import Path
from founder.evaluation.dataset import load_labeled_dataset
from founder.evaluation.metrics import compute_ndcg, compute_mrr, compute_recall


def run_experiment():
    """Load labeled dataset and compute retrieval metrics.

    This is a manual/demo version. Full experiment framework with
    Langfuse tracking is Step 25's job.
    """

    labeled_path = Path(
        "data/05_evaluation/retrieval_questions.json"
    )

    if not labeled_path.exists():

        print(
            f"Dataset not found: {labeled_path}\n"
            "Run with data/05_evaluation/retrieval_questions.json "
            "that contains 'relevant_evidence_ids' field."
        )

        return

    try:

        questions = load_labeled_dataset(labeled_path)

    except Exception as error:

        print(f"Failed to load dataset: {error}")

        return

    if not questions:

        print("No labeled questions found in dataset.")
        return

    print(f"\n== Retrieval Evaluation ==\n")
    print(f"Questions: {len(questions)}")

    print(f"\nNote: Full ground-truth labeling (relevant_evidence_ids)")
    print(f"is manual work. These are sample metrics computed over")
    print(f"whatever labels exist in the dataset.\n")

    for question in questions[:3]:

        print(
            f"Q {question.question_id}: "
            f"{question.question[:60]}..."
        )

        print(
            f"  Relevant evidence IDs: {len(question.relevant_evidence_ids)}"
        )

        if not question.relevant_evidence_ids:
            print("  (no labels yet)")

        print()

    print(
        "To run full retrieval evaluation with real metrics:\n"
        "1. Label retrieval_questions.json with relevant_evidence_ids\n"
        "2. Call load_labeled_dataset() and compute_ndcg/mrr/recall\n"
        "3. Integrate with Langfuse (Step 25)\n"
    )


if __name__ == "__main__":
    run_experiment()
