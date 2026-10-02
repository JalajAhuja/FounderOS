# Step 21 — Fiscal Period Resolution

## Goal

Map arbitrary publication dates to canonical fiscal periods (FY/Q), and
harmonize XBRL fact periods so "Revenue in FY2025 Q2" is unambiguous across
different filing schedules and reconciliations.

## Non-goals

- Handling non-calendar fiscal years (e.g., Costco's Q1 = Sep-Nov) — deferred
  to Step 33.
- Reclassification/normalization of XBRL fields (e.g., "net income" vs.
  "consolidated net income") — that's a data-quality pipeline, not this step.

## Inputs

- Chunk publication dates + (year/quarter metadata when present).
- XBRL facts with fiscal_year/fiscal_period fields + period end dates.
- Corporate fiscal calendars (SEC CIK → fiscal year-end).

## Outputs

```text
src/founder/storage/
├── __init__.py
├── fiscal_cache.py
└── period_mapping.py

src/founder/retrieval/
├── fact_resolution.py
└── fact_resolution_test.py
```

Public API: `resolve_fiscal_period`, `get_fiscal_calendar`, `harmonize_periods`.

## Architecture

```text
publication_date + metadata
    ↓
resolve_fiscal_period()
    ↓
check cache for ticker -> fiscal_year_end
    ↓
map (month, day) to (FY, Q)
    ↓
return canonical "2025-Q2" or "FY2025"
```

## Files to create

```text
src/founder/storage/__init__.py
src/founder/storage/fiscal_cache.py
src/founder/retrieval/fact_resolution.py
src/founder/retrieval/fact_resolution_test.py
tests/retrieval/__init__.py (if missing)
tests/storage/__init__.py
tests/storage/test_period_mapping.py
```

## Files to modify

```text
src/founder/reasoning/dates.py  (use resolve_fiscal_period as authoritative
                                 instead of fallback to published_at)
```

## Data contracts

Fiscal calendar dict:

```json
{
  "MSFT": {"fiscal_year_end_month": 6},
  "AAPL": {"fiscal_year_end_month": 9}
}
```

Resolution output:

```python
{
  "canonical": "FY2025-Q2",
  "fiscal_year": 2025,
  "fiscal_quarter": 2,
  "period_start": "2024-10-01",
  "period_end": "2024-12-31",
  "basis": "fiscal_calendar" | "metadata" | "published_at" | "unknown"
}
```

## Error handling

- Calendar lookup failure falls back to published_at approximation (flag as
  basis="published_at").
- Unparseable dates return basis="unknown", period="unknown".

## Observability

Log (warn level) when falling back from fiscal calendar to published_at, so
operator can see data quality issues.

## Tests

- `tests/storage/test_period_mapping.py`: MSFT (Jun year-end), calendar
  lookup, period boundary logic, unknown cases.

## Acceptance criteria

- `python -m founder.retrieval.fact_resolution_test` runs and maps sample
  dates to fiscal periods.
- `python -m pytest -q` passes without live services.

## Rollback / recovery

`resolve_fiscal_period` is optional (fall back to published_at basis in
`reasoning.dates` if not available).

## Known limitations

- Fiscal calendar is hardcoded (not SEC-derived); Step 33 uses SEC data.
- No handling of non-calendar fiscal years (Costco, Adobe fiscal Q1 ≠
  calendar Q1).
