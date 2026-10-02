# Step 19 — Tracing & Observability

## Goal

Capture structured execution traces for every query, enabling observability,
debugging, and reproducibility without relying on logs or print statements.

## Non-goals

- Real-time dashboarding (that's UI/Langfuse integration layers).
- Sampling or truncation (keep all traces).

## Inputs

- `FounderState` (Step 11), `Evidence` (Step 10), `GeneratedAnswer` (Step 18).

## Outputs

```text
src/founder/observability/
├── __init__.py
├── tracer.py
├── models.py
└── langfuse_integration.py
```

Public API: `get_tracer()`, `Trace` (pydantic model), `trace_node()` decorator.

## Architecture

```text
Every node execution -> trace_node wrapper
  -> event recorded with (node_name, input, output, latency, error)
-> Final trace object combines all events
   + metadata (query, query_plan, model config, etc.)
-> Optional: push to Langfuse for remote storage
```

## Files to create

```text
src/founder/observability/__init__.py
src/founder/observability/tracer.py
src/founder/observability/models.py
src/founder/observability/langfuse_integration.py
tests/observability/__init__.py
tests/observability/test_tracer.py
src/founder/observability/test_trace.py (manual verification CLI)
```

## Files to modify

```text
src/founder/agent/nodes.py        (wrap each node with trace_node)
src/founder/agent/graph.py        (attach trace metadata)
src/founder/agent/runner.py       (print trace summary)
```

## Data contracts

```python
class TraceEvent(BaseModel):
    timestamp: float
    node_name: str
    event_type: Literal["start", "end", "error"]
    latency_ms: float | None
    input_sample: dict | None
    output_sample: dict | None
    error: str | None

class Trace(BaseModel):
    trace_id: str
    request_id: str
    query: str
    model_config: dict
    prompt_version: str
    events: list[TraceEvent]
    total_latency_ms: float
    final_answer_tokens: int | None
    error: str | None
    langfuse_trace_id: str | None
```

## Error handling

- Tracing failures never propagate (wrap all tracer calls in try/except).
- If Langfuse push fails, log warning but don't abort query execution.

## Observability

- Trace objects are JSON-serializable and stored for reproducibility (Step 22).
- Optional Langfuse export for real-time analysis (via optional `LANGFUSE_PUBLIC_KEY`).

## Tests

- `tests/observability/test_tracer.py`: trace creation, event recording, latency
  calculation, JSON serialization, no live Langfuse required.

## Acceptance criteria

- Every node wraps input/output/latency/error in a `TraceEvent`.
- `python -m founder.observability.test_trace` runs a sample query and prints
  a summary trace.
- `python -m pytest -q` passes without Langfuse credentials.

## Rollback / recovery

Wrap entire tracing layer in a single runtime flag (`TRACING_ENABLED`);
setting `TRACING_ENABLED=false` disables all tracer calls without code changes.

## Known limitations

- Trace size grows with evidence count (no sampling yet).
- No distributed tracing across multiple services (single process only).
