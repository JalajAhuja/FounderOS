# Step 22 — Export & Serialization

## Goal

Deterministically serialize traces, answers, and evidence into JSON for
reproducibility, storage, and API responses. No randomness, no circular
references, all timestamps/scores/IDs embedded.

## Non-goals

- Pretty-printing / user-facing display (that's Step 23+ UI work).
- Real-time streaming export (that's Step 24).

## Inputs

- `Trace` objects (Step 19), `GeneratedAnswer` (Step 18), `Evidence` (Step 10).

## Outputs

```text
src/founder/export/
├── __init__.py
├── serialization.py
└── models.py
```

Public API: `serialize_answer`, `serialize_trace`, `serialize_evidence`,
`serialize_full_response`.

## Architecture

```text
query execution
    ↓
final Trace + Answer + Evidence
    ↓
serialize_full_response()
    ↓
deterministic JSON (all UUIDs, timestamps, IDs embedded)
    ↓
store for reproducibility / API response
```

## Files to create

```text
src/founder/export/__init__.py
src/founder/export/serialization.py
src/founder/export/models.py
tests/export/__init__.py
tests/export/test_serialization.py
```

## Files to modify

```text
src/founder/agent/runner.py  (add export_response() call)
```

## Data contracts

Full response serialization:

```json
{
  "trace_id": "t123",
  "query": "What did Microsoft say about AI?",
  "answer": {
    "text": "...",
    "claims": [
      {
        "text": "...",
        "evidence_ids": ["qdrant:chunk-1"],
        "claim_type": "source_claim",
        "confidence": 0.9
      }
    ],
    "citations": [
      {
        "citation_id": 1,
        "evidence_id": "qdrant:chunk-1",
        "source": "earnings_call",
        "date": "2025-06-01"
      }
    ],
    "limitations": [...]
  },
  "evidence": [
    {
      "evidence_id": "qdrant:chunk-1",
      "source": "qdrant",
      "text": "...",
      "score": 0.87,
      "ticker": "MSFT",
      "published_at": "2025-06-01",
      "metadata": {}
    }
  ],
  "trace": {
    "trace_id": "t123",
    "events": [...],
    "total_latency_ms": 1500
  }
}
```

## Error handling

- Circular references are replaced with `"<circular>"` placeholders.
- Non-JSON-serializable types are converted via `str()` or omitted.

## Observability

None; this is the output layer.

## Tests

- `tests/export/test_serialization.py`: Evidence serialization, Answer
  serialization, Trace serialization, full response serialization,
  reproducibility (same input -> same JSON string).

## Acceptance criteria

- `python -m founder.export.test_export` runs and produces valid JSON.
- `python -m pytest -q` passes without live services.
- Same query input (+ same timestamp) produces identical JSON output
  (deterministic).

## Rollback / recovery

Export is read-only; no rollback needed.

## Known limitations

- Determinism requires fixing timestamps/UUIDs — done via an optional
  override mechanism (not shown), used only in tests.
- Large evidence sets (hundreds of chunks) produce large JSON; Step 32 adds
  compression.
