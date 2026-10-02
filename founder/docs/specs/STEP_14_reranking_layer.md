# Step 14 — Reranking Layer

## Goal

Add a cross-encoder reranking stage between broad Qdrant hybrid retrieval
and the final evidence set handed to the agent.

## Non-goals

- Full evaluation framework with relevance-labeled ground truth (Step 20).
- Reranking graph/XBRL results (only Qdrant candidates are noisy enough at
  volume to benefit; graph/facts results are already small and precise).

## Inputs

- `HybridRetriever.search()` (Step 10, unchanged).
- `data/05_evaluation/retrieval_questions.json` (ticker/source expectations
  only — no relevance-labeled chunk IDs yet).

## Outputs

- `founder.retrieval.reranker.Reranker` — `.rerank(query, documents, top_k)`.
- Wired into `founder.agent.tools.vector_tool.search_qdrant`: retrieves
  `max(top_k, RERANK_CANDIDATES)` candidates, then reranks down to `top_k`.
- `python -m founder.evaluation.evaluate_retrieval` — manual before/after
  comparison script.

## Architecture

```text
Qdrant dense + sparse -> up to RERANK_CANDIDATES (30) candidates
                       -> Reranker (cross-encoder)
                       -> top FINAL_TOP_K (8) evidence
```

Uses `fastembed.rerank.cross_encoder.TextCrossEncoder` (already available
via the installed `fastembed` dependency — no new package required),
model configurable via `RERANKER_MODEL` (default
`Xenova/ms-marco-MiniLM-L-6-v2`, a small locally-cached ONNX cross-encoder).
`RERANKER_ENABLED` (default `true`) and candidate/top_k sizes are all
environment-configurable, never hard-coded to an unavailable model.

## Files to create

```text
src/founder/retrieval/reranker.py
src/founder/evaluation/__init__.py
src/founder/evaluation/evaluate_retrieval.py
tests/retrieval/__init__.py
tests/retrieval/test_reranker.py
```

## Files to modify

```text
src/founder/agent/tools/vector_tool.py   (candidate retrieval -> rerank)
requirements.txt                         (added qdrant-client, fastembed,
                                           neo4j, openai -- already used by
                                           Steps 10/13 code but missing
                                           from requirements.txt)
```

`UnifiedRetriever`/`HybridRetriever` (Step 10) are untouched — only the
agent's `search_qdrant` tool applies reranking, so Step 10's manual REPL
behavior is unchanged.

## Data contracts

```python
class Reranker:
    def rerank(self, query: str, documents: list[Evidence], top_k: int) -> list[Evidence]: ...
```

Each returned `Evidence.metadata["rerank_score"]` is set to the
cross-encoder's raw score for observability.

## Error handling

If the cross-encoder model can't be loaded/downloaded (offline
environment, first-run download failure), `rerank()` catches the
exception, prints a warning, and falls back to the original ordering
truncated to `top_k` — reranking is never a hard dependency for retrieval
to function.

## Observability

`rerank_score` stored on each reranked `Evidence.metadata` for later
inspection/tracing (Step 19).

## Tests

- `tests/retrieval/test_reranker.py`: disabled reranker is a pass-through;
  a fake model's scores actually reorder documents; a failing model falls
  back to original order; empty input returns empty output. No live model
  download required — the cross-encoder call is monkeypatched.

## Acceptance criteria

- Reranking never processes more than `RERANK_CANDIDATES` documents.
- `python -m founder.evaluation.evaluate_retrieval` runs (against a live
  Qdrant) and prints a proxy match-rate metric with/without reranking.
- `python -m pytest -q` passes without a live Qdrant or a downloaded model.

## Rollback / recovery

Set `RERANKER_ENABLED=false` to fully disable reranking without code
changes; `search_qdrant` still requests `RERANK_CANDIDATES` internally,
but the pass-through reranker just truncates to `top_k` unchanged.

## Known limitations

- `evaluate_retrieval.py` reports a ticker/source match-rate proxy, not
  true Recall@k/MRR@k, because `retrieval_questions.json` has no
  relevance-labeled evidence IDs — building that labeled dataset is part
  of Step 20.
- The default cross-encoder model is downloaded from Hugging Face on
  first use and cached locally; fully offline environments must
  pre-populate the fastembed cache or set `RERANKER_ENABLED=false`.
