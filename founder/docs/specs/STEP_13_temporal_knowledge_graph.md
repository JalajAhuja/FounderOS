# Step 13 — Better GraphRAG + Temporal Knowledge Graph

## Goal

Harden the Neo4j prototype from Step 10 into a provenance-preserving
temporal graph: every extracted relationship keeps its full evidence
history instead of being overwritten by the next chunk that mentions the
same two entities, and that evidence is traceable through explicit graph
edges (not just relationship properties) down to a source `Document`.

## Non-goals

- LLM extraction quality/prompt changes (schema/prompt already existed;
  only new structural relationship types were added, not new LLM-visible
  entity/relationship types).
- Computing true `valid_to` end dates for relationships (requires the
  temporal reasoning engine, Step 15) — `valid_to` is left `null` (open)
  and `valid_from` is a best-effort equal to the source chunk's
  `published_at`, not a fiscal-period-aware value (Step 21 concern).
- Reprocessing already-written graph data — this step changes how future
  `write_graph` runs behave; existing Neo4j data written under the old
  schema is not migrated (`docker compose down -v` + re-run
  `init_graph`/`write_graph` to get the hardened shape).
- Changing `GraphRetriever`'s retrieval Cypher (Step 10) — relationship
  properties it already reads (`evidence`, `confidence`, `chunk_id`, etc.)
  are unchanged in shape, so no consumer code needed updates.

## Inputs

- `data/04_chunks/graph_extractions.jsonl` (unchanged producer:
  `founder.graph.extract_entities`).
- Existing `founder.graph.neo4j_client.Neo4jClient`.

## Outputs

- Hardened `founder.graph.write_graph` that preserves relationship history
  per source chunk and creates explicit `Document`/`PART_OF`/`SUPPORTED_BY`
  provenance edges.
- `founder.graph.timeline` — `get_company_timeline`,
  `get_relationship_timeline`, `compare_periods`,
  `find_new_relationships`, `find_removed_relationships`.
- `python -m founder.graph.timeline_test` manual verification script.

## Architecture

```text
(:Company)-[:INVESTS_IN {chunk_id, evidence, confidence, ticker,
                          published_at, valid_from, valid_to}]->(:Technology)

(:Company)-[:SUPPORTED_BY]->(:Chunk)-[:PART_OF]->(:Document)
(:Technology)-[:SUPPORTED_BY]->(:Chunk)-[:PART_OF]->(:Document)
```

The direct entity-to-entity edge (e.g. `INVESTS_IN`) is kept — it is what
`GraphRetriever` already queries — but its **identity now includes
`chunk_id`**, so the same (source, type, target) triple extracted from two
different chunks produces two separate, independently timestamped edges
instead of the second `MERGE` silently overwriting the first's evidence.
`SUPPORTED_BY` is an additive, explicit entity -> Chunk edge created for
every entity that participates in an extracted relationship (distinct
from the pre-existing generic `MENTIONED_IN` edge, which is created for
every mentioned entity regardless of relationship participation). Combined
with the new `Chunk -[:PART_OF]-> Document` edge, this gives a fully
graph-native provenance trace: entity -> relationship -> `SUPPORTED_BY` ->
Chunk -> `PART_OF` -> Document -> `published_at`, without requiring a
property-based join as the only way to find the source.

## Files to create

```text
src/founder/graph/timeline.py
src/founder/graph/timeline_test.py
tests/graph/__init__.py
tests/graph/test_timeline.py
tests/graph/test_write_graph.py
```

## Files to modify

```text
src/founder/graph/schema.py       (added STRUCTURAL_NODE_TYPES,
                                    STRUCTURAL_RELATIONSHIP_TYPES for
                                    documentation; RELATIONSHIP_TYPES is
                                    now the single source of truth)
src/founder/graph/write_graph.py  (ALLOWED_RELATIONSHIPS now derived from
                                    schema.RELATIONSHIP_TYPES instead of a
                                    second hand-maintained set;
                                    create_document + Chunk PART_OF edge;
                                    create_relationship keyed by chunk_id
                                    with valid_from/valid_to;
                                    create_supported_by helper)
src/founder/graph/init_graph.py   (added Chunk/Document published_at
                                    indexes for timeline query performance)
```

## Data contracts

Relationship properties (unchanged keys, two new ones added):

```text
evidence, confidence, document_id, source, ticker, published_at,
valid_from (new), valid_to (new, currently always null)
```

`get_company_timeline` / `get_relationship_timeline` row shape:

```json
{
  "source": "Microsoft",
  "relationship": "INVESTS_IN",
  "target": "OpenAI",
  "evidence": "...",
  "confidence": 0.9,
  "chunk_id": "...",
  "document_id": "...",
  "source_type": "earnings",
  "ticker": "MSFT",
  "published_at": "2025-06-01",
  "valid_from": "2025-06-01",
  "valid_to": null
}
```

`compare_periods` output:

```json
{
  "period_a": {"start": "...", "end": "...", "relationships": [...]},
  "period_b": {"start": "...", "end": "...", "relationships": [...]},
  "added": [["Microsoft", "ACQUIRED", "Activision"]],
  "removed": [["Microsoft", "PARTNERS_WITH", "Nokia"]],
  "unchanged": [["Microsoft", "COMPETES_WITH", "Google"]]
}
```

## Error handling

- `create_document` is a no-op when `document_id` is missing (some
  extraction records could theoretically lack it) rather than raising.
- All `timeline.py` functions accept an optional `client` so callers can
  reuse a connection and handle connection errors themselves; when no
  client is passed, the function owns and closes its own connection even
  on exception (`try/finally`).

## Observability

No new logging beyond what `write_graph.main()` already prints
(chunks/entities/relationships processed counts).

## Tests

- `tests/graph/test_write_graph.py`: verifies (with a fake client that
  just records executed Cypher/params, no live Neo4j) that
  `create_chunk` also creates a `Document` and `PART_OF` edge,
  `create_relationship` scopes the merge key by `chunk_id` and sets
  `valid_from`, creates two `SUPPORTED_BY` edges, and still rejects
  unknown relationship types.
- `tests/graph/test_timeline.py`: verifies each of the 5 helper functions
  against a fake Neo4j driver (records the Cypher issued, returns canned
  rows) — no live Neo4j required, consistent with Steps 11/12's testing
  approach.

## Acceptance criteria

- A relationship can be traced: entity -> relationship -> evidence chunk
  (via `chunk_id` property, and independently via the new `SUPPORTED_BY`
  edge) -> source document (via `PART_OF`) -> publication date.
- Re-running `write_graph` on the same extractions file is idempotent
  (same chunk_id -> same merged edge), but two different chunks describing
  the same relationship type between the same two entities produce two
  distinct, separately timestamped edges rather than one overwritten edge.
- `python -m pytest -q` passes without a live Neo4j instance.

## Rollback / recovery

- All changes are additive to the write path; `GraphRetriever` (Step 10)
  and `graph_retriever` consumers are unaffected because relationship
  property names and the direct entity-to-entity edge shape are unchanged.
- Reverting `create_relationship`'s merge key to `(s)-[r:TYPE]->(t)`
  (dropping `{chunk_id: $chunk_id}` from the pattern) restores the old
  overwrite-on-conflict behavior if needed.

## Known limitations

- `valid_from`/`valid_to` are populated from chunk `published_at`, not
  fiscal period — comparing "FY2025 Q2" vs. a news article's crawl date
  requires Step 21's period resolution work.
- `compare_periods`/`find_new_relationships`/`find_removed_relationships`
  operate on raw `published_at` string comparisons; they assume the stored
  format sorts correctly lexicographically (true for the `YYYY-MM-DD`-style
  dates already produced upstream, but not validated against other
  formats).
- Existing graph data written before this step does not have `valid_from`
  or a chunk-scoped relationship identity; a full graph rebuild
  (`python -m founder.graph.init_graph` then `write_graph`) is required to
  get the hardened shape for historical data.
- `SUPPORTED_BY` provenance edges are only created for entities that
  participate in an extracted *relationship*; entities that are only
  mentioned (no relationship) still rely on the pre-existing
  `MENTIONED_IN` edge for their own provenance.
