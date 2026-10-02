# Step 24 — Streaming + Agent Trace UI

## Goal

Stream query execution progress to client in real-time without exposing
hidden chain-of-thought reasoning.

## Non-goals

- Expose raw LLM reasoning
- Debug-level logs to UI
- Real-time graph updates

## Inputs

- LangGraph agent with instrumentation (Step 19)
- Existing agent runner
- Event tracking from observability layer

## Outputs

```text
src/founder/api/
├── routes/
│   └── stream.py
└── schemas/
    └── stream.py
```

Streaming endpoint: `POST /api/v1/query/stream`

## Architecture

```text
Frontend                Backend (FastAPI)           Agent
    │                         │                      │
    └─── POST /query/stream ──────────────────────►│
                              │◄─ start processing ─┤
                              │                      │
                         (monitor events)
                              │
                         emit: "analyzing"
                              │ ──────────────────► [Analyzing query]
                              │
                         emit: "retrieving"
                              │ ──────────────────► [Searching financial...]
                              │
                         emit: "evidence"
                              │ ──────────────────► [Evidence: chunk-123]
                              │
                         emit: "reasoning"
                              │ ──────────────────► [Checking consistency]
                              │
                         emit: "generating"
                              │ ──────────────────► [Generating answer]
                              │
                         emit: "complete"
                              │ ──────────────────► [Final answer + citations]
```

## Event types

```python
StatusEvent
  - type: "status"
  - message: str
  - timestamp: datetime

EvidenceEvent
  - type: "evidence"
  - evidence_id: str
  - source: str (SEC, earnings_call, news, graph)
  - ticker: str
  - date: str

AnswerEvent
  - type: "answer"
  - text: str
  - complete: bool

CompleteEvent
  - type: "complete"
  - trace_id: str
  - latency_ms: int
  - answer: str
  - evidence_count: int

ErrorEvent
  - type: "error"
  - error_message: str
  - trace_id: str
```

## Message format

Server-sent events (SSE):

```
data: {"type": "status", "message": "Analyzing query...", "timestamp": "2026-09-30T10:00:00Z"}

data: {"type": "evidence", "evidence_id": "qdrant:chunk-123", "source": "SEC", "ticker": "MSFT", "date": "2025-06-01"}

data: {"type": "answer", "text": "Microsoft's AI strategy...", "complete": true}

data: {"type": "complete", "trace_id": "t123", "latency_ms": 1234, "answer": "...", "evidence_count": 5}
```

## User-visible messages

Do NOT expose:

- LLM prompts
- Intermediate reasoning
- Database query syntax
- Internal error traces

DO expose:

```text
Analyzing query...
Searching financial filings (SEC)...
Searching earnings calls...
Searching knowledge graph...
Checking prior periods...
Verifying consistency...
Generating answer...
Done!
```

## Implementation

1. Wrap agent execution in event capture
2. Stream events as SSE
3. Frontend listens to stream and updates UI
4. Final answer sent as "complete" event

## Error handling

- If stream closes unexpectedly: client reconnects
- If backend error: send ErrorEvent and close stream
- If timeout: send error and close stream

## Observability

- Track event emission timing
- Record which events were sent
- Log stream closes/errors

## Tests

- Mock agent execution
- Verify event stream produced
- Test error conditions
- Verify client receives all events

## Acceptance criteria

- `POST /api/v1/query/stream` returns streaming response
- Events emit in correct order
- Frontend displays status updates in real-time
- Final response contains complete answer

## Rollback / recovery

Fallback to non-streaming endpoint if stream fails.

## Known limitations

- Timeline visualization not included (deferred to Step 25)
- No interactive debugging UI
- Events are one-way (no client→server during stream)
