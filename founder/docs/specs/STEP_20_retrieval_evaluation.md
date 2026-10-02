# Step 20 — Retrieval Evaluation

## Goal

Build a ground-truth evaluation dataset with relevance labels, and compute
retrieval metrics (NDCG, MRR, Recall@k) to measure performance vs baseline.

## Non-goals

- End-to-end answer evaluation (faithfulness, entailment) — that's Step 23+.
- User feedback loops (that's Step 25+).

## Inputs

- Existing `data/05_evaluation/retrieval_questions.json` (now we add
  `relevant_evidence_ids[]` to each question).
- Existing retrieval implementations (Qdrant, Graph, XBRL).

## Outputs

```text
src/founder/evaluation/
├── __init__.py
├── metrics.py
├── dataset.py
└── run_experiment.py
```

Public API: `compute_ndcg`, `compute_mrr`, `compute_recall`,
`load_labeled_dataset`, `run_retrieval_experiment`.

## Architecture

```text
labeled_questions.json (with relevant_evidence_ids)
          ↓
load_labeled_dataset()
          ↓
for each question:
  for each retriever:
    retrieve top_k
    compute_ndcg/mrr/recall vs ground truth
          ↓
print summary table
```

## Files to create

```text
src/founder/evaluation/__init__.py
src/founder/evaluation/metrics.py
src/founder/evaluation/dataset.py
src/founder/evaluation/run_experiment.py
tests/evaluation/__init__.py
tests/evaluation/test_metrics.py
data/05_evaluation/retrieval_questions_labeled.json (example with labels)
```

## Files to modify

```text
data/05_evaluation/retrieval_questions.json  (add relevant_evidence_ids)
```

## Data contracts

Enhanced retrieval_questions.json:

```json
[
  {
    "id": "q001",
    "question": "What did Microsoft say about AI monetization?",
    "expected_tickers": ["MSFT"],
    "expected_sources": ["SEC", "earnings_call"],
    "relevant_evidence_ids": [
      "qdrant:chunk-123",
      "qdrant:chunk-456",
      "graph:relationship-789"
    ]
  }
]
```

Metrics output:

```json
{
  "question_id": "q001",
  "retriever": "qdrant",
  "retrieved_ids": ["qdrant:chunk-456", "..."],
  "ndcg@5": 0.92,
  "ndcg@10": 0.87,
  "mrr@5": 0.80,
  "recall@5": 0.5,
  "recall@10": 0.8
}
```

## Error handling

- Questions without `relevant_evidence_ids` are skipped (not an error).
- Retrievers that fail are marked with `error: "..."` in results.

## Observability

Print a summary table with mean/std across all questions and retrievers.

## Tests

- `tests/evaluation/test_metrics.py`: NDCG calculation, MRR, Recall with
  known ground truth (no live retrieval required).

## Acceptance criteria

- `python -m founder.evaluation.run_experiment` runs and prints a metrics
  table.
- At least three retrievers are benchmarked (qdrant, graph, facts).
- `python -m pytest -q` passes without live services.

## Rollback / recovery

Evaluation is read-only; no rollback needed.

## Known limitations

- No multi-query pooling / inter-question relevance yet.
- No per-retriever parameter tuning (fixed top_k).
- Labels are manual (no crowdsourcing or LLM-generated labels yet).
