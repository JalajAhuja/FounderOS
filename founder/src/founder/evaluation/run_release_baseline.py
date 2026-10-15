"""Write a reproducible, dependency-light release baseline report."""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from founder.evaluation.dataset import load_labeled_dataset
from founder.evaluation.metrics import compute_mrr, compute_ndcg, compute_recall


def _version() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run(output: str | Path = "docs/evaluation/BASELINE.md") -> Path:
    path = Path("data/05_evaluation/retrieval_questions.json")
    questions = load_labeled_dataset(path) if path.exists() else []
    labeled = [question for question in questions if question.relevant_evidence_ids]
    report = ["# FounderOS Release Baseline", "", f"- Generated: {datetime.now(timezone.utc).isoformat()}", f"- Commit: {_version()}", f"- Dataset: {path}", f"- Questions: {len(questions)}", f"- Labeled questions: {len(labeled)}", ""]
    if not labeled:
        report += ["## Metrics", "No labeled retrieval results are available yet. Metrics remain zero until the evaluation set contains `retrieved_evidence_ids` and `relevant_evidence_ids`.", ""]
    else:
        values = {"Recall@5": 0.0, "Recall@10": 0.0, "MRR@10": 0.0, "NDCG@10": 0.0}
        for question in labeled:
            retrieved = getattr(question, "retrieved_evidence_ids", [])
            values["Recall@5"] += compute_recall(retrieved, question.relevant_evidence_ids, 5)
            values["Recall@10"] += compute_recall(retrieved, question.relevant_evidence_ids, 10)
            values["MRR@10"] += compute_mrr(retrieved, question.relevant_evidence_ids, 10)
            values["NDCG@10"] += compute_ndcg(retrieved, question.relevant_evidence_ids, 10)
        report += ["## Metrics"] + [f"- {key}: {value / len(labeled):.4f}" for key, value in values.items()] + [""]
    report += ["## Known Limitations", "- Answer, temporal, graph, latency, and cost metrics require a live experiment run and are not inferred here.", "- A baseline is comparable only when model, prompt, index, and dataset versions are held constant.", ""]
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    print(run())
