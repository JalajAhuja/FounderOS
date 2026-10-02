# Step 17 — Evidence Sufficiency + Corrective Retrieval

## Goal

Replace the Step 11 "evidence non-empty = sufficient" placeholder with
real sufficiency signals (coverage, source diversity, temporal coverage,
entity coverage, directness, contradiction count), and replace the
"broaden everything" corrective retrieval with strategy selection targeted
at what is actually missing.

## Non-goals

- LLM-based query rewriting/paraphrasing — `query_rewriter.broaden_query`
  is a deterministic regex-based period-qualifier stripper, not a
  semantic rewrite.
- Changing the hard retry limit — `MAX_RETRIEVAL_ROUNDS = 2` (Step 11)
  is unchanged; this step only changes what happens *within* a corrective
  round.

## Inputs

- `query_plan` (Step 12), `evidence` (Steps 11/14), `contradictions`
  (Step 16, present only if a contradiction-check pass has already run in
  the current graph traversal).

## Outputs

```text
src/founder/agent/sufficiency.py
src/founder/agent/query_rewriter.py
src/founder/agent/corrective.py
```

## Architecture

```text
grade_evidence: assess_sufficiency(plan, evidence, contradictions)
   -> {sufficient, reason[], missing[], evidence_count, source_diversity,
       temporal_coverage, entity_coverage, directness, contradiction_count}

corrective_retrieval: build_corrective_plan(plan, missing, query)
   -> targeted plan/source broadening + broadened query text
   -> only re-runs the sources actually present in the new plan
```

`missing` signal -> strategy mapping:

```text
any_evidence     -> ticker_expansion + source_expansion (all 4 sources)
prior_period     -> period_expansion (adds graph/qdrant/timeline)
external_event   -> news_fallback (adds news)
financial_fact   -> fact_fallback (adds facts)
```

## Files to create

```text
src/founder/agent/sufficiency.py
src/founder/agent/query_rewriter.py
src/founder/agent/corrective.py
tests/agent/test_sufficiency.py
tests/agent/test_corrective.py
tests/agent/test_query_rewriter.py
```

## Files to modify

```text
src/founder/agent/nodes.py  (grade_evidence_node -> assess_sufficiency;
                              corrective_retrieval_node -> build_corrective_plan,
                              and only searches sources present in the
                              corrected plan instead of always all four)
```

## Data contracts

```json
{
  "sufficient": false,
  "reason": ["Only one reporting period found."],
  "missing": ["prior_period"],
  "evidence_count": 3,
  "source_diversity": 2,
  "temporal_coverage": 1,
  "entity_coverage": 1,
  "directness": 1.0,
  "contradiction_count": 0
}
```

## Error handling

Unchanged from Step 11: each corrective search call is wrapped in
try/except and degrades to an error entry rather than aborting the round.

## Observability

`retrieval_runs` entries created during a corrective round now include a
`strategies` list so it's visible which corrective strategies fired.

## Tests

- `tests/agent/test_sufficiency.py`: insufficient when no evidence;
  sufficient for a simple satisfied plan; insufficient when temporal
  comparison needs a second period; insufficient when external events are
  requested but no news evidence exists; insufficient when a factual
  question has no XBRL evidence.
- `tests/agent/test_corrective.py`: each `missing` signal maps to its
  expected source/strategy addition; no-missing-signals is a no-op.
- `tests/agent/test_query_rewriter.py`: period qualifiers are stripped;
  queries without them are returned unchanged.

## Acceptance criteria

- The agent terminates after at most `MAX_RETRIEVAL_ROUNDS` even when
  evidence remains insufficient (unchanged Step 11 guarantee, now paired
  with real sufficiency grading rather than a trivial non-empty check).
- When evidence remains insufficient after the retry, the final answer
  states the limitation instead of guessing (see Step 18 — `synthesize`
  appends the sufficiency reason to `limitations`).
- `python -m pytest -q` passes without live services.

## Rollback / recovery

`grade_evidence_node`/`corrective_retrieval_node` changes are localized;
reverting them to the Step 11 versions (non-empty check, broaden-everything)
requires no changes elsewhere in the graph.

## Known limitations

- `contradictions` is empty on the first grading pass in the current
  graph topology (`grade_evidence` runs before `contradiction_check`), so
  `contradiction_count` is only meaningful if sufficiency were
  re-assessed after contradiction detection — not currently wired that
  way; documented rather than restructuring the graph in this step.
- `query_rewriter.broaden_query` only strips explicit year/quarter/FY
  tokens; it does not perform synonym expansion or true paraphrasing.
