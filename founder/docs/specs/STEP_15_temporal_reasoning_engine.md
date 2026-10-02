# Step 15 — Temporal Reasoning Engine

## Goal

Compare evidence across two reporting periods and produce a structured
before/after change summary, replacing the Step 11 placeholder that only
grouped evidence by year.

## Non-goals

- Graph-level temporal queries (`founder.graph.timeline`, Step 13) — this
  engine operates on `Evidence` records already retrieved, not on Neo4j
  relationship history directly.
- Causal inference — differences are reported as observed changes, never
  as "caused by" claims.
- Fiscal-period-aware date resolution (Step 21) — periods are inferred
  from chunk `year`/`quarter` metadata when present (authoritative) or
  parsed from `published_at` as a documented fallback (not authoritative).

## Inputs

- `Evidence` objects (already carry `published_at` and, for Qdrant-sourced
  evidence, `metadata["year"]`/`metadata["quarter"]` from the chunk
  payload; for XBRL facts, `metadata` carries `fiscal_year`/
  `fiscal_period`).

## Outputs

```text
src/founder/reasoning/__init__.py
src/founder/reasoning/dates.py
src/founder/reasoning/claims.py
src/founder/reasoning/comparisons.py
src/founder/reasoning/temporal.py
```

Public API: `normalize_period`, `group_by_period`, `compare_periods`,
`detect_change`, `build_change_summary`.

## Architecture

```text
evidence -> normalize_period (fiscal metadata > published_at fallback)
         -> group_by_period
         -> detect_change (fact-value diff + top-narrative diff)
         -> build_change_summary
```

`reasoning.claims` provides a shared, deterministic (non-LLM) sentence-level
claim extractor reused by both this step and Step 16's contradiction
detection, so the two features don't duplicate text-splitting logic.

## Files to create

See "Outputs" above, plus:

```text
tests/reasoning/__init__.py
tests/reasoning/test_dates.py
tests/reasoning/test_temporal.py
```

## Files to modify

```text
src/founder/agent/nodes.py  (temporal_reasoning_node now calls
                              reasoning.temporal.compare_periods when the
                              plan needs a temporal comparison and >=2
                              periods are present, in addition to the
                              existing build_timeline overview)
```

## Data contracts

```json
{
  "topic": "AI monetization",
  "period_a": "2025-Q2",
  "period_b": "2026-Q1",
  "changes": [
    {
      "dimension": "monetization",
      "before": "...",
      "after": "...",
      "evidence_ids": ["...", "..."]
    }
  ]
}
```

`normalize_period(evidence)` returns
`{"period": "2025-Q2", "basis": "fiscal"|"published_at"|"unknown",
"year": 2025, "quarter": 2}`.

## Error handling

`parse_date` returns `None` on unparseable input rather than raising;
`normalize_period` falls back to `"unknown"` period in that case, and
`group_by_period` always sorts `"unknown"` last rather than raising on a
comparison between a period string and `None`.

## Observability

None beyond the structured objects themselves; full tracing is Step 19.

## Tests

- `tests/reasoning/test_dates.py`: date parsing (ISO, RSS-style),
  fiscal-metadata-preferred period normalization, published_at fallback,
  unknown case.
- `tests/reasoning/test_temporal.py`: `group_by_period` chronological
  ordering, `detect_change` fact-value diffing, `compare_periods` full
  structured output, `build_change_summary` shape.

## Acceptance criteria

- For "What changed in Microsoft's AI strategy between 2025 and 2026?"
  (with evidence spanning both years already retrieved), the agent's
  `temporal_context.comparison` separates Period A / Period B / Change /
  Evidence per the JSON contract above.
- `python -m pytest -q` passes without live services.

## Rollback / recovery

`temporal_reasoning_node`'s call to `compare_periods` is additive and
gated on `needs_temporal_comparison` + >=2 periods; removing that branch
restores the exact Step 11/12 `build_timeline`-only behavior.

## Known limitations

- `compare_periods` currently compares only the earliest and latest
  observed periods among retrieved evidence, not every adjacent pair.
- `compare_text_snippets` picks the single highest-scoring narrative
  statement per period rather than synthesizing across several — a
  coverage-level, not semantic-diff, comparison.
- Period inference from `published_at` (when fiscal metadata is absent)
  assumes the publication date approximates the fiscal period, which is
  explicitly flagged via `basis="published_at"` but not corrected.
