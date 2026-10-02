# Step 32 — Evidence Pack / Export

## Goal
Export a source-backed investigation as stable Markdown or JSON.
## Non-goals
PDF generation, new retrieval behavior, or hidden model reasoning.
## Inputs
Query results containing answer, claims, evidence, timeline, facts, and trace ID.
## Outputs
`InvestigationPack` and `artifacts/investigation_<timestamp>.md`.
## Architecture
Normalize result -> typed pack -> deterministic human-readable Markdown or JSON.
## Files to create
`export/models.py`, `export/investigation.py`, `export/__main__.py`.
## Files to modify
`export/__init__.py`.
## Data contracts
Sources and claims retain their stable evidence IDs.
## Error handling
Missing result fields become explicit empty sections and limitations.
## Observability
Trace IDs are preserved when supplied.
## Tests
`tests/export/test_investigation.py` plus existing serialization tests.
## Acceptance criteria
`python -m founder.export investigation --query "..."` writes a readable pack.
## Rollback / recovery
Existing JSON serialization remains available independently.
## Known limitations
The CLI creates an empty pack unless a caller supplies live agent results.