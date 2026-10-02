# Step 34 — Final Evaluation / Regression Baseline

## Goal
Record reproducible retrieval metrics and version context.
## Non-goals
Manufacturing labels or live answer quality metrics without an experiment.
## Inputs
The labeled retrieval dataset and current Git commit.
## Outputs
`docs/evaluation/BASELINE.md`.
## Architecture
Load labels -> compute Recall, MRR, and NDCG when retrieval IDs exist -> write report.
## Files to create
`src/founder/evaluation/run_release_baseline.py`.
## Files to modify
None.
## Data contracts
The report records commit, dataset path, question counts, and metric definitions.
## Error handling
Missing data or Git metadata produces a valid report with explicit unknown/zero values.
## Observability
Generation timestamp and version identifiers are recorded.
## Tests
Existing evaluation metric tests and the module smoke command.
## Acceptance criteria
`python -m founder.evaluation.run_release_baseline` always produces a report.
## Rollback / recovery
Regenerate the report after correcting labels or index versions.
## Known limitations
End-to-end answer, latency, and cost metrics require a live run.