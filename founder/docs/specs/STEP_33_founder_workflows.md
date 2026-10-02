# Step 33 — Founder Workflow Features

## Goal
Provide explicit company, comparison, change-monitor, and strategy-brief query contracts.
## Non-goals
Adding new databases or pretending a workflow is evidence by itself.
## Inputs
Slash command plus ticker arguments.
## Outputs
`WorkflowRequest` and runner metadata.
## Architecture
Command parser -> auditable query template -> existing agent runner.
## Files to create
`src/founder/workflows.py` and its tests.
## Files to modify
None.
## Data contracts
Workflow name, normalized tickers, and expanded query are returned.
## Error handling
Invalid commands raise an actionable `ValueError`.
## Observability
Workflow name and tickers can be attached to the existing trace.
## Tests
`tests/test_workflows.py`.
## Acceptance criteria
All four documented commands produce deterministic requests.
## Rollback / recovery
Call the agent directly; workflow parsing is additive.
## Known limitations
UI command autocomplete and persistence are future integration work.