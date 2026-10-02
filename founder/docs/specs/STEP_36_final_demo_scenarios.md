# Step 36 — Final Demo Scenarios

## Goal
Define five demonstrations that exercise semantic, fact, graph, temporal, and strategic paths.
## Non-goals
Presenting unsupported conclusions as facts.
## Inputs
The configured corpus, services, API, and frontend.
## Outputs
Repeatable queries and evidence-backed responses.
## Architecture
Each scenario exposes which retriever and reasoning layer was used.
## Files to create
This specification and the final README scenario list.
## Files to modify
None beyond documentation.
## Data contracts
Every material claim must map to retrieved evidence and a citation.
## Error handling
Incomplete evidence must become a limitation or uncertainty statement.
## Observability
Capture trace ID, retrieval plan, latency, and evidence IDs for each demo.
## Tests
Run the full Python suite and manually exercise the API/UI.
## Acceptance criteria
All five scenario queries are documented with expected architectural signals.
## Rollback / recovery
Use the prior baseline and retain captured traces.
## Known limitations
Results depend on corpus coverage and running Qdrant/Neo4j services.