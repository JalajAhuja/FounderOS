# Step 31 — External Event / News Quality Hardening

## Goal
Turn stored news metadata into conservative, provenance-preserving event records.
## Non-goals
Scraping or redistributing publisher article text, or asserting causality from timing.
## Inputs
`data/03_primary/news.jsonl` records with title, URL, domain, ticker, and publication date.
## Outputs
Typed `Event` records and date-window queries in `founder.news`.
## Architecture
Metadata -> keyword category -> stable event/evidence IDs -> deduplication -> timeline query.
## Files to create
`src/founder/news/{events,event_resolution,timeline}.py`.
## Files to modify
News consumers may import the new package; no existing retrieval contract changes.
## Data contracts
Every event retains document, evidence, URL, domain, ticker, date, and confidence.
## Error handling
Blank titles and unparseable dates are skipped or return an empty date query.
## Observability
Event IDs and source metadata are included in exported evidence.
## Tests
`tests/news/test_events.py`.
## Acceptance criteria
Events can be traced back to a news document and queried around a date.
## Rollback / recovery
Remove the package; the original news retriever remains usable.
## Known limitations
Categories are deterministic keyword classifications, not semantic event extraction.