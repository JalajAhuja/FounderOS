# Step 18 — Answer Synthesis + Citation Engine

## Goal

Generate answers as a structured claims + citations + limitations
contract instead of Step 11's free-text answer, and guarantee — by
construction, not just by prompting — that no claim can cite evidence that
wasn't actually retrieved and no citation can carry an invented date or
source.

## Non-goals

- Streaming token-by-token output (Step 24).
- Full evaluation of faithfulness/citation precision (Step 20).

## Inputs

- `evidence` (post-rerank, Step 14), `sufficiency` (Step 17).

## Outputs

```text
src/founder/generation/__init__.py
src/founder/generation/schemas.py
src/founder/generation/citations.py
src/founder/generation/prompts.py
src/founder/generation/answer.py
```

`generate_answer(query, evidence, sufficiency=None) -> GeneratedAnswer`.

## Architecture

```text
evidence -> format_evidence_block (id=... source=... ticker=... date=...)
         -> LLM call with strict JSON-schema response_format
            (answer, claims[{text, evidence_ids, claim_type, confidence}],
             limitations[])
         -> validate: drop any claim whose evidence_ids are not a subset
            of the evidence actually retrieved; drop claims left with zero
            valid evidence_ids
         -> citations.build_citations(): deterministically derive
            citation_id/source/date from the Evidence objects themselves
            (never from the model's output)
         -> append a sufficiency-derived limitation when evidence was
            graded insufficient (Step 17)
```

Uses the same direct-`OpenAI`-client + `response_format=json_schema`
pattern already established in `founder.graph.extract_entities`, rather
than introducing a second structured-output convention.

## Files to create

See "Outputs" above.

## Files to modify

```text
src/founder/agent/nodes.py   (synthesize_node calls
                               founder.generation.answer.generate_answer)
src/founder/agent/state.py   (FounderState gained `claims` and
                               `limitations` fields)
src/founder/agent/runner.py  (prints claims/limitations)
```

Removed `src/founder/agent/prompts.py` (Step 11's ad hoc synthesis
prompt/call) — fully superseded by `founder.generation`.

## Data contracts

```json
{
  "answer": "...",
  "claims": [
    {
      "text": "...",
      "evidence_ids": ["qdrant:chunk-123"],
      "claim_type": "source_claim",
      "confidence": 0.84
    }
  ],
  "citations": [
    {
      "citation_id": 1,
      "evidence_id": "qdrant:chunk-123",
      "citation_text": "[1]",
      "source": "earnings_call",
      "date": "2025-06-01"
    }
  ],
  "limitations": ["Evidence coverage may be incomplete: ..."]
}
```

`claim_type` is one of `fact | source_claim | inference | uncertainty`.

## Error handling

- If the LLM call raises, `synthesize_node` catches it and returns a
  deterministic error answer plus `limitations: ["Answer generation
  failed."]` rather than propagating the exception through the graph.
- With no evidence at all, `generate_answer` short-circuits before
  calling the LLM and returns "I don't have enough evidence..." plus a
  `limitations` entry.

## Observability

None beyond the structured objects; full tracing is Step 19.

## Tests

- `tests/generation/test_citations.py`: stable citation IDs in
  first-appearance order; unknown evidence IDs are skipped.
- `tests/generation/test_answer.py`: no-evidence fallback; hallucinated
  evidence IDs are dropped from a claim; a claim left with zero valid IDs
  is dropped entirely; an insufficiency reason is appended to
  `limitations`. The OpenAI client is faked (monkeypatched), no live API
  key required.

## Acceptance criteria

- No citation in the final output can reference an `evidence_id` that
  wasn't in the retrieved evidence set for that query.
- `python -m pytest -q` passes without a live OpenAI key.
- `python -m founder.agent.runner` prints `answer`, evidence count,
  numbered citations, limitations, and errors (when present).

## Rollback / recovery

`synthesize_node` calling `founder.generation.answer.generate_answer` is a
single import + call swap; the previous `agent/prompts.generate_answer`
implementation is fully superseded and was removed rather than kept
duplicated.

## Known limitations

- `claim_type`/`confidence` are model-reported, not independently
  verified — Step 20's faithfulness evaluation is needed to validate them
  at scale.
- Citation `citation_text` is always the bracketed index (`[1]`); richer
  citation formatting (e.g., inline accession numbers for SEC filings) is
  left for the future export/UI work (Steps 22/23/32).
