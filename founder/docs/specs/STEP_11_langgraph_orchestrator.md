# Step 11 — LangGraph Agentic Orchestrator

## Goal

Turn the existing `UnifiedRetriever` (Qdrant + Neo4j + XBRL) into a stateful,
typed LangGraph workflow that plans retrieval, checks evidence sufficiency,
performs one bounded corrective retrieval round, applies lightweight temporal
and contradiction pre-processing, and synthesizes a cited answer.

## Non-goals

- Full retrieval planner with per-intent tool selection (Step 12).
- Provenance-hardened temporal knowledge graph queries (Step 13).
- Real reranking layer (Step 14).
- Full temporal reasoning engine (Step 15) — this step only groups evidence
  by period as context, it does not compute before/after change summaries.
- Full contradiction detection (Step 16) — this step only wires the node and
  performs a trivial same-topic polarity check as a placeholder.
- Full sufficiency/corrective retrieval strategies (Step 17) — this step
  implements one bounded retry with source broadening only.
- Full answer/citation schema with claim typing (Step 18).
- Observability/Langfuse integration (Step 19).

## Inputs

- Existing modules: `founder.retrieval.hybrid_search.HybridRetriever`,
  `founder.retrieval.fact_retriever.FactRetriever`,
  `founder.retrieval.graph_retriever.GraphRetriever`,
  `founder.retrieval.query_analyzer.analyze_query`,
  `founder.retrieval.evidence.Evidence`.
- `OPENAI_API_KEY` / `OPENAI_GRAPH_MODEL` env vars (via `founder.graph.config`
  pattern; the agent defines its own `AGENT_MODEL` env var with a safe
  default so it does not silently reuse the graph-extraction model config).

## Outputs

- `src/founder/agent/` package producing a compiled LangGraph app.
- `python -m founder.agent.runner` — interactive REPL, same shape as
  `founder.retrieval.test_unified`.
- Structured result per query:

```json
{
  "answer": "...",
  "evidence": [...],
  "citations": [...],
  "retrieval_plan": {...}
}
```

## Architecture

```text
START -> analyze_query -> plan_retrieval
plan_retrieval -> qdrant_search, graph_search, xbrl_search   (fan-out)
qdrant_search, graph_search, xbrl_search -> normalize_evidence (fan-in)
normalize_evidence -> grade_evidence
grade_evidence -[insufficient, rounds < limit]-> corrective_retrieval -> grade_evidence
grade_evidence -[sufficient OR rounds >= limit]-> temporal_reasoning
temporal_reasoning -> contradiction_check -> synthesize -> END
```

Each search node reads `state["query_plan"]["sources"]` and only performs
its retrieval if its source key is present, otherwise returns no evidence.
This keeps orchestration (LangGraph) separate from tool implementation
(`agent/tools.py`), which itself only wraps the already-existing retriever
classes — it does not duplicate their logic.

Database/model clients (`HybridRetriever`, `FactRetriever`, `GraphRetriever`)
are constructed once as a module-level `RetrieverBundle` singleton in
`agent/tools.py` and reused across graph invocations, avoiding reconnecting
to Qdrant/Neo4j or reloading embedding models per query.

## Files to create

```text
src/founder/agent/__init__.py
src/founder/agent/state.py
src/founder/agent/tools.py
src/founder/agent/nodes.py
src/founder/agent/routing.py
src/founder/agent/graph.py
src/founder/agent/prompts.py
src/founder/agent/config.py
src/founder/agent/runner.py
tests/agent/__init__.py
tests/agent/test_state.py
tests/agent/test_nodes.py
tests/agent/test_graph_shape.py
```

## Files to modify

```text
src/founder/retrieval/query_analyzer.py   (pre-existing bug fix — see below)
src/founder/retrieval/evidence.py         (add qdrant_to_evidence helper)
```

### Pre-existing bug found and fixed

`src/founder/retrieval/query_analyzer.py` contained an accidental duplicate
of `fact_retriever.py` (no `analyze_query` function existed), even though
`unified_retriever.py` imports `analyze_query` from it. This made the
existing Step-10 retriever unusable. Fixed by implementing the intended
keyword-based `analyze_query(query, known_tickers)` classifier returning
`{query, ticker, sources, is_fact, is_graph, is_temporal, is_strategic}`,
matching the contract already consumed by `UnifiedRetriever.search()`.

## Data contracts

```python
class FounderState(TypedDict):
    query: str
    query_plan: dict
    evidence: Annotated[list[Evidence], operator.add]
    retrieval_runs: Annotated[list[dict], operator.add]
    temporal_context: dict  
    contradictions: list[dict]
    sufficiency: dict
    answer: str | None
    citations: list[dict]
    errors: Annotated[list[str], operator.add]
    trace_id: str | None
```

`evidence`, `retrieval_runs`, and `errors` use an additive reducer so the
three fanned-out search nodes (and the corrective retry) can each append
independently without clobbering each other's updates.

## Error handling

- Each search node wraps its retriever call in `try/except`; failures are
  recorded as `{"errors": [f"<node>: <message>"]}` partial updates and the
  node returns empty evidence rather than raising, so one broken retriever
  does not fail the whole graph.
- `synthesize` catches LLM call failures and falls back to a deterministic
  "insufficient evidence" answer citing the error.
- `RetrieverBundle` construction failures (e.g. Neo4j down) are caught at
  `runner.py` startup and reported clearly before entering the REPL.

## Observability

- Each node appends a `retrieval_runs` entry: `{"node": ..., "count": ...,
  "latency_ms": ...}`. Full Langfuse tracing is deferred to Step 19; this
  step only guarantees the state shape needed for it.

## Tests

- `test_state.py`: constructing `FounderState` partial updates merges lists
  via the `operator.add` reducer as expected.
- `test_nodes.py`: unit tests for `plan_retrieval`, `grade_evidence`,
  `temporal_reasoning`, and `contradiction_check` using fake `Evidence`
  objects (no live Qdrant/Neo4j/OpenAI calls).
- `test_graph_shape.py`: the compiled graph exposes the expected nodes and
  can be built without invoking it (no live services required).
- Retriever-dependent and OpenAI-dependent paths are exercised manually via
  `python -m founder.agent.runner` (requires local Qdrant/Neo4j + API key),
  consistent with how `test_unified.py` is already verified.

## Acceptance criteria

- `python -m pytest -q` passes without requiring Qdrant/Neo4j/OpenAI.
- `python -m founder.agent.runner` answers "What did Microsoft say about AI
  monetization?" and prints `answer`, `evidence`, `citations`,
  `retrieval_plan` when live services are available.
- The graph never loops more than `MAX_RETRIEVAL_ROUNDS = 2` times.

## Rollback / recovery

- The new `agent/` package is additive; `UnifiedRetriever` and
  `test_unified.py` remain unchanged and usable independently.
- The `query_analyzer.py` fix is a strict bug fix restoring the documented
  contract already relied upon by `unified_retriever.py`; reverting it
  would restore the pre-existing broken import.

## Known limitations

- Corrective retrieval only broadens sources to include all three
  retrievers; it does not yet do query rewriting, ticker expansion, or
  period expansion (Step 17).
- Temporal reasoning only groups evidence by year/quarter; it does not
  compute structured before/after change summaries (Step 15).
- Contradiction check is a placeholder heuristic, not full claim extraction
  and pairwise conflict detection (Step 16).
- Synthesis uses a single-shot prompt without the full claim/citation
  schema (Step 18) or evaluation harness (Step 20).
