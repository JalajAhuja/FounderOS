# Step 25 — Production Persistence / Checkpointing

## Goal

Persist session state, query history, and agent checkpoints so FounderOS can
recover from restarts and provide audit trails.

## Non-goals

- Full multi-user collaboration (that's a future step)
- Distributed session management
- Real-time cache invalidation

## Inputs

- LangGraph agent with checkpointing hooks
- FastAPI request/response lifecycle
- Feedback from users (Step 23)

## Outputs

```text
src/founder/storage/
├── __init__.py
├── postgres.py
├── models.py
└── repositories.py

src/founder/api/
└── dependencies.py
    (inject session/db context)
```

## Architecture

PostgreSQL schema:

```sql
sessions
  - session_id (UUID, PK)
  - created_at (timestamp)
  - updated_at (timestamp)
  - user_id (string, nullable)
  - status (active | closed)

queries
  - query_id (UUID, PK)
  - session_id (FK)
  - query_text (string)
  - created_at (timestamp)

agent_runs
  - run_id (UUID, PK)
  - query_id (FK)
  - checkpoint_data (JSONB, LangGraph state)
  - status (pending | complete | error)
  - started_at (timestamp)
  - completed_at (timestamp)
  - latency_ms (integer)
  - error (string, nullable)

answers
  - answer_id (UUID, PK)
  - run_id (FK)
  - answer_text (string)
  - claims (JSONB)
  - citations (JSONB)
  - evidence (JSONB)

feedback
  - feedback_id (UUID, PK)
  - run_id (FK)
  - rating (1-5)
  - comment (string, nullable)
  - created_at (timestamp)
```

## Files to create

```text
src/founder/storage/__init__.py (updated)
src/founder/storage/postgres.py
src/founder/storage/models.py
src/founder/storage/repositories.py

src/founder/api/dependencies.py

tests/storage/test_postgres.py
tests/storage/test_repositories.py
```

## Data contracts

Session creation:

```python
session = create_session(user_id="optional")
# → Session(session_id, created_at, status="active")
```

Query logging:

```python
query_record = log_query(session_id, query_text)
# → QueryRecord(query_id, session_id, query_text, created_at)
```

Agent run checkpoint:

```python
checkpoint = save_checkpoint(query_id, checkpoint_data)
# → AgentRun(run_id, query_id, checkpoint_data, status="pending")
```

Answer persistence:

```python
answer_record = save_answer(run_id, answer, claims, citations, evidence)
# → Answer(answer_id, run_id, answer_text, ...)
```

Feedback:

```python
feedback_record = save_feedback(run_id, rating, comment)
# → Feedback(feedback_id, run_id, rating, comment, created_at)
```

## Error handling

- DB connection failure: log and continue (graceful degradation)
- Foreign key constraint: validate before insert
- Transaction rollback: retry once

## Observability

- Log session creation/closure
- Track checkpoint save frequency
- Measure DB latency

## Tests

- Create/retrieve session
- Log query
- Save checkpoint
- Retrieve checkpoint for recovery
- Save/retrieve answer
- Save/retrieve feedback
- Transaction consistency

## Acceptance criteria

- `pytest -q` passes with PostgreSQL tests
- Sessions persist across restarts
- Checkpoints can be loaded and resumed
- Full audit trail available

## Setup

Connection string from env:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/founder
```

## Rollback / recovery

If DB unavailable, system continues with in-memory state.
History is only lost if DB is also unrecoverable.

## Known limitations

- No distributed transactions across multiple DBs
- No time-travel queries (point-in-time recovery is manual)
- Session sharing not implemented (user isolation via user_id only)
