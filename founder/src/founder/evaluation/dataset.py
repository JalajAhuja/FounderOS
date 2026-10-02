"""Load and manage evaluation datasets with relevance labels."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LabeledQuestion:

    question_id: str
    question: str
    relevant_evidence_ids: list[str]
    expected_tickers: list[str] | None = None


def load_labeled_dataset(path: str | Path) -> list[LabeledQuestion]:
    """Load evaluation questions with relevance labels from JSON."""

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = []

    for item in data:

        if "relevant_evidence_ids" not in item:
            continue

        questions.append(
            LabeledQuestion(
                question_id=item.get("id", "unknown"),
                question=item.get("question", ""),
                relevant_evidence_ids=item.get(
                    "relevant_evidence_ids", []
                ),
                expected_tickers=item.get("expected_tickers"),
            )
        )

    return questions
