# Step 12 — Retrieval Planner + Specialized Tools

## Goal

Convert query analysis into an explicit, deterministic, executable
retrieval plan, and reorganize ad hoc retrieval wrappers into a proper
`agent/tools/` package with one file per source.

## Non-goals

- Reranking of candidates returned by any tool (Step 14).
- Provenance-hardened temporal knowledge graph (Step 13) — `timeline_tool`
  only groups evidence already retrieved by other tools; it runs no Cypher
  of its own.
- Full external-event extraction/classification (Step 31) — `news_tool`
  does simple keyword/ticker filtering over `data/03_primary/news.jsonl`.
- LLM-based intent classification — the planner is a deterministic keyword
  classifier so its output is reproducible for a fixed query.

## Inputs

- `founder.retrieval.query_analyzer.analyze_query` (Step 11) for
  ticker/flag extraction.
- Existing retriever classes: `HybridRetriever`, `FactRetriever`,
  `GraphRetriever`.
- New: `founder.retrieval.news_retriever.NewsRetriever` over
  `data/03_primary/news.jsonl`.

## Outputs

- `founder.agent.planner.build_retrieval_plan(query, known_tickers)` →
  `{query, ticker, intent, sources, needs_temporal_comparison,
  needs_external_events, is_fact, is_graph, is_temporal, is_strategic}`.
- `src/founder/agent/tools/` package: `base.py`, `vector_tool.py`,
  `graph_tool.py`, `fact_tool.py`, `news_tool.py`, `timeline_tool.py`.
- A `news_search` node in the agent graph, wired into the same
  fan-out/fan-in pattern as `qdrant_search`/`graph_search`/`xbrl_search`.

## Architecture

```text
analyze_query_node   -> raw flags (unchanged from Step 11, kept for
                         observability/backwards compatibility)
plan_retrieval_node   -> founder.agent.planner.build_retrieval_plan(...)
                         (this is now the authoritative query_plan)
```

Intent classification priority (most to least specific):

```text
temporal > relationship > factual > strategic > semantic (default)
```

Source selection per intent:

```text
factual      -> [facts]
semantic     -> [qdrant]
relationship -> [graph]
temporal     -> [graph, qdrant, timeline]
strategic    -> [facts, graph, qdrant] (+ news if external events detected)
```

`needs_external_events` is detected independently of intent and adds
`news` to any plan's sources when present (e.g. a temporal or relationship
question that also asks about announcements/regulatory events).

`timeline` is not a retrieval node — it signals `temporal_reasoning_node`
to call `agent.tools.timeline_tool.build_timeline()` over whatever
evidence `qdrant_search`/`graph_search` already returned.

## Files to create

```text
src/founder/retrieval/news_retriever.py
src/founder/agent/planner.py
src/founder/agent/tools/__init__.py
src/founder/agent/tools/base.py
src/founder/agent/tools/vector_tool.py
src/founder/agent/tools/graph_tool.py
src/founder/agent/tools/fact_tool.py
src/founder/agent/tools/news_tool.py
src/founder/agent/tools/timeline_tool.py
tests/agent/test_planner.py
tests/agent/test_news_retriever.py
```

## Files to modify

```text
src/founder/agent/nodes.py     (plan_retrieval_node now calls the planner;
                                 added news_search_node; corrective
                                 retrieval broadens to include news;
                                 temporal_reasoning_node delegates to
                                 timeline_tool.build_timeline)
src/founder/agent/graph.py     (wire news_search into fan-out/fan-in)
src/founder/retrieval/evidence.py (added news_to_evidence helper)
tests/agent/test_graph_shape.py   (expect news_search node)
tests/agent/test_nodes.py         (plan_retrieval_node test updated —
                                    it is no longer a no-op)
```

Removed `src/founder/agent/tools.py` (single module), replaced by the
`tools/` package — Python cannot have both a module and a package with the
same import path.

## Data contracts

```python
class ToolResult:
    success: bool
    evidence: list[Evidence]
    metadata: dict
    latency_ms: float
```

```json
{
  "query": "...",
  "ticker": "MSFT",
  "intent": "temporal",
  "sources": ["graph", "qdrant", "timeline"],
  "needs_temporal_comparison": true,
  "needs_external_events": false,
  "is_fact": false,
  "is_graph": false,
  "is_temporal": true,
  "is_strategic": false
}
```

## Error handling

Unchanged from Step 11: each search node (including the new
`news_search_node`) wraps its call in try/except and degrades to empty
evidence + an error entry rather than failing the graph.
`plan_retrieval_node` catches `RetrieverBundle` construction failures the
same way `analyze_query_node` already did.

## Observability

`retrieval_runs` now also includes `news_search` entries. No other change
to the Step 11 observability shape.

## Tests

- `tests/agent/test_planner.py`: deterministic intent/source assignment
  for one example query per category (factual, semantic, relationship,
  temporal, strategic+external-events), plus a determinism check
  (same query -> identical plan across two calls).
- `tests/agent/test_news_retriever.py`: loads the real
  `data/03_primary/news.jsonl` and verifies ticker filtering (no live
  services required — this is a local data file, same as
  `FactRetriever`'s existing pattern).
- `tests/agent/test_nodes.py`: `plan_retrieval_node` produces the expected
  plan shape, with `RetrieverBundle` mocked out via monkeypatch (no live
  services required).
- `tests/agent/test_graph_shape.py`: updated to expect the `news_search`
  node in the compiled graph.

## Acceptance criteria

- `build_retrieval_plan` is deterministic: the same query always returns
  the same plan.
- The plan (including `intent` and `sources`) is fully computed before any
  retrieval executes.
- `python -m founder.agent.runner` prints a `retrieval_plan` containing
  `intent`, `sources`, `needs_temporal_comparison`, and
  `needs_external_events` for each manual test query.

## Rollback / recovery

- `analyze_query_node` is left intact, so reverting `plan_retrieval_node`
  to a no-op restores exact Step 11 behavior (raw flags only, no `intent`
  field, sources chosen by the simple keyword union).
- `agent/tools/` is a strict reorganization of the Step 11 `tools.py`
  module plus additive `news_tool.py`/`timeline_tool.py` — all Step 11
  public names (`get_bundle`, `ToolResult`, `search_qdrant`,
  `search_facts`, `search_graph`) are still importable from
  `founder.agent.tools`.

## Known limitations

- The planner is keyword-based; ambiguous queries that mix intents (e.g.
  a strategic question phrased with "change") are classified via a fixed
  priority order, not a learned or LLM-based classifier.
- `timeline_tool.build_timeline` only groups by publication year, not
  fiscal period, and does not yet reconcile publication date vs. fiscal
  period (Step 15 / Step 21 concerns).
- `NewsRetriever` matches on article titles only (no full article body is
  ingested), consistent with the existing `01_raw/news` data.
