# Step 16 — Contradiction Detection

## Goal

Detect conflicting claims across retrieved evidence and surface them
explicitly, rather than silently merging them into one answer — replacing
the Step 11 placeholder that only flagged "same section, multiple
sources" without checking whether the statements actually disagreed.

## Non-goals

- LLM-based claim extraction/NLI (kept deterministic and heuristic, same
  tradeoff as Step 15's `reasoning.claims`).
- `scope_difference` / `metric_definition_difference` classification —
  the heuristic here can only reliably distinguish `direct_conflict` /
  `apparent_conflict` / `change_over_time` via keyword polarity + period
  comparison; the other two types require deeper semantic understanding
  and are left as known limitations.

## Inputs

- `reasoning.claims.extract_all_claims` (Step 15).

## Outputs

```text
src/founder/reasoning/contradictions.py
```

`detect_contradictions(evidence_list) -> list[dict]`.

## Architecture

```text
evidence -> extract_all_claims -> group by (ticker, section)
         -> pairwise polarity comparison
         -> classify (direct_conflict | apparent_conflict | change_over_time)
         -> contradiction report
```

Polarity is a small positive/negative keyword-set heuristic. Two claims in
the same (ticker, section) group with opposite polarity are:

- `change_over_time` if they fall in different coarse (year, quarter)
  periods — explicitly **not** treated as a contradiction, matching the
  plan's example ("Q2: growth was 20%" vs "Q4: growth was 12%" is a
  change, not a contradiction).
- `direct_conflict` if same period and different sources.
- `apparent_conflict` if same period and same source (weaker signal).

## Files to create

```text
src/founder/reasoning/contradictions.py
tests/reasoning/test_contradictions.py
```

## Files to modify

```text
src/founder/agent/nodes.py  (contradiction_check_node now calls
                              detect_contradictions instead of the
                              Step 11 same-section/multi-source placeholder)
```

## Data contracts

```json
{
  "claim_a": "...",
  "claim_b": "...",
  "type": "direct_conflict",
  "evidence_a": ["..."],
  "evidence_b": ["..."],
  "time_relation": "same",
  "severity": "medium"
}
```

## Error handling

Claims with no detectable polarity keyword are skipped (not flagged) —
absence of a signal is not treated as a conflict signal.

## Observability

None beyond the structured contradiction objects; full tracing is Step 19.

## Tests

- `tests/reasoning/test_contradictions.py`: same-period opposite-polarity
  claims -> `direct_conflict`; different-quarter opposite-polarity claims
  -> `change_over_time`; no polarity keywords -> no contradiction;
  different sections -> no contradiction (not grouped together).
- `tests/agent/test_nodes.py` updated: the old placeholder test is
  replaced with one exercising real keyword-based conflict detection.

## Acceptance criteria

- For the conflicting-source example in the architecture doc ("Demand is
  accelerating" vs. "Demand remains uncertain"), `detect_contradictions`
  surfaces both statements as a `direct_conflict`/`apparent_conflict`.
- `python -m pytest -q` passes without live services.

## Rollback / recovery

`contradiction_check_node`'s call is a one-line swap; reverting to the
Step 11 placeholder (same-section/multi-source flagging) requires no
other changes.

## Known limitations

- Keyword-based polarity is coarse; sarcasm, negated positives ("not
  slowing down"), and domain-specific terms outside the keyword lists are
  not detected.
- `scope_difference`/`metric_definition_difference` are not implemented.
- Grouping by `(ticker, section)` means contradictions across differently
  labeled sections about the same real-world topic are missed.
