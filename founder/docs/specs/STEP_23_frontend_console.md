# Step 23 — Frontend / Founder Intelligence Console

## Goal

Create a polished UI for querying FounderOS and displaying structured answers
with evidence, citations, and timeline visualization.

## Non-goals

- Generic chat interface (we're building a financial intelligence tool)
- Real-time collaborative editing
- Advanced charting (timeline only)

## Inputs

- Existing FastAPI backend (Step 22)
- `/api/v1/query` POST endpoint
- `/api/v1/health` GET endpoint

## Outputs

```text
frontend/
├── package.json
├── src/
│   ├── index.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── QueryInput.tsx
│   │   ├── AnswerDisplay.tsx
│   │   ├── EvidenceCard.tsx
│   │   ├── Citations.tsx
│   │   ├── Timeline.tsx
│   │   └── Filters.tsx
│   ├── services/
│   │   └── api.ts
│   ├── styles/
│   │   └── globals.css
│   └── types/
│       └── index.ts
├── public/
│   └── index.html
└── vite.config.ts (or next.config.js)
```

## Architecture

```text
React Frontend
    │
    ├── QueryInput → /api/v1/query POST
    ├── AnswerDisplay (formatted markdown/citations)
    ├── EvidenceCard (SEC, Earnings, News, Graph)
    ├── Timeline (visual periods)
    ├── Filters (ticker, source, date range)
    └── Feedback (rate answer)
```

## Files to create

```text
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── src/index.tsx
├── src/App.tsx
├── src/components/QueryInput.tsx
├── src/components/AnswerDisplay.tsx
├── src/components/EvidenceCard.tsx
├── src/components/Citations.tsx
├── src/components/Timeline.tsx
├── src/components/Filters.tsx
├── src/services/api.ts
├── src/types/index.ts
└── src/styles/globals.css
```

## Data contracts

Request:

```json
{
  "query": "What changed in Microsoft's AI monetization?",
  "top_k": 8,
  "filters": {
    "tickers": ["MSFT"],
    "sources": ["SEC", "earnings_call"],
    "date_from": "2025-01-01",
    "date_to": "2026-12-31"
  }
}
```

Response:

```json
{
  "trace_id": "t123",
  "query": "...",
  "answer": "...",
  "claims": [...],
  "citations": [...],
  "evidence": [...],
  "retrieval_plan": {...},
  "latency_ms": 1234
}
```

## UI Layout

```
┌───────────────────────────────────────────────────────────┐
│ FounderOS                                  ● System Ready │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ Ask a strategic question...                               │
│ [Query Input Field]          [Filters ▼]  [Ask]          │
│                                                           │
├────────────────────────────┬──────────────────────────────┤
│ Answer                     │ Evidence                     │
│                            │                              │
│ [Formatted answer with]    │ [Evidence Cards]             │
│ citations [1][2][3]        │ ├─ SEC filing (date)        │
│                            │ ├─ Earnings call (date)     │
│                            │ └─ News (date)              │
│                            │                              │
├────────────────────────────┴──────────────────────────────┤
│ Timeline                                                   │
│ 2025 Q2 ───── 2025 Q4 ───── 2026 Q1                      │
│      statement      change       latest statement          │
│                                                           │
│ Status: Supported by 4 sources | 2 periods | No conflicts│
└───────────────────────────────────────────────────────────┘
```

## Error handling

- Network errors: show retry button
- Invalid query: show validation error
- Backend timeout: show "Please try simpler query"
- Health check failed: show "System unavailable"

## Observability

- Track page load time
- Track query latency
- Track user interactions (search, filter, feedback)
- Send to Langfuse (via backend)

## Tests

- Component render tests (React Testing Library)
- API service tests (mock fetch)
- Integration test with real backend

## Acceptance criteria

- Frontend loads and connects to backend /health
- Query input accepts text
- Submit button sends POST /api/v1/query
- Response displays answer + citations
- Evidence cards show source, date, text
- Timeline visualization renders

## Rollback / recovery

Frontend is stateless; can always revert to previous version.

## Known limitations

- No graph visualization (Step 24+)
- No real-time collaboration
- Timeline is text-based, not interactive
