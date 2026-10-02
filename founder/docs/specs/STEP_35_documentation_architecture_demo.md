# Step 35 — Documentation / Architecture / Demo

## Goal
Make the hybrid architecture and demo scenarios understandable to a new developer.
## Non-goals
Changing runtime behavior.
## Inputs
Implemented ingestion, retrieval, graph, agent, API, frontend, and evaluation modules.
## Outputs
Architecture and operational documentation.
## Architecture
The docs mirror the evidence-first path from query to cited response.
## Files to create
`docs/{architecture,data_model,retrieval,agent,evaluation,deployment,limitations}.md`.
## Files to modify
Repository README.
## Data contracts
Docs refer to stable evidence IDs, citations, traces, and evaluation reports.
## Error handling
Known unavailable services and incomplete datasets are documented.
## Observability
Trace and baseline locations are documented.
## Tests
Documentation review plus the project test suite.
## Acceptance criteria
A new developer can run the documented checks and understand service boundaries.
## Rollback / recovery
Documentation changes are independently revertible.
## Known limitations
Screenshots and live service results depend on local infrastructure.