# FounderOS — Remaining Implementation Plan (Step 11 → Final)

> **Purpose:** This file is the execution contract for GitHub Copilot. Give this entire file to Copilot and instruct it to implement **one step at a time, in order**.
>
> **Important:** Copilot must not skip ahead. After each step, it must create the requested spec file, implement the code, add/update tests, and stop so the developer can run the verification commands below.

---

## 0. Current Project State

The project has already completed the following layers:

1. SEC ticker/company metadata ingestion
2. SEC submissions metadata
3. SEC filing selection
4. SEC filing download
5. SEC HTML cleaning
6. Canonical SEC `documents.jsonl`
7. SEC XBRL facts `facts.jsonl`
8. Earnings call `earnings.jsonl`
9. News `news.jsonl`
10. Source-aware chunking `chunks.jsonl`
11. Chunk validation
12. Qdrant dense + sparse hybrid indexing
13. Neo4j graph prototype / graph extraction
14. Unified retrieval prototype combining Qdrant + Neo4j + XBRL

Assumed important paths:

```text
founder/
├── data/
│   ├── 01_raw/
│   │   ├── sec/
│   │   ├── earnings/
│   │   └── news/
│   ├── 03_primary/
│   │   ├── documents.jsonl
│   │   ├── facts.jsonl
│   │   ├── earnings.jsonl
│   │   └── news.jsonl
│   ├── 04_chunks/
│   │   ├── chunks.jsonl
│   │   ├── sec_chunks.jsonl
│   │   ├── earnings_chunks.jsonl
│   │   ├── news_chunks.jsonl
│   │   └── graph_extractions.jsonl
│   └── 05_evaluation/
│       └── retrieval_questions.json
│
├── src/
│   └── founder/
│       ├── ingestion/
│       ├── retrieval/
│       └── graph/
│
├── docker-compose.yml
├── .env
└── .gitignore
```

Current infrastructure:

```text
Qdrant   http://localhost:6333
Neo4j    http://localhost:7474
Neo4j   bolt://localhost:7687
```

---

# 1. Global Instructions for GitHub Copilot

For every step below, Copilot must follow this workflow:

### Step A — Read current code first

Before changing anything:

- inspect the existing repository
- identify already implemented files
- reuse existing interfaces where possible
- do not duplicate retrievers, configs, or database clients
- do not silently rename existing public interfaces
- do not delete working functionality

### Step B — Create a spec for the step

Create:

```text
docs/specs/STEP_XX_<short_name>.md
```

Every step spec must contain:

```text
# Step XX — <Name>

## Goal
## Non-goals
## Inputs
## Outputs
## Architecture
## Files to create
## Files to modify
## Data contracts
## Error handling
## Observability
## Tests
## Acceptance criteria
## Rollback / recovery
## Known limitations
```

### Step C — Implement

Implement only the current step.

### Step D — Test

Add unit/integration tests appropriate to the step.

### Step E — Stop

Do not continue to the next step until the developer runs the verification commands and confirms success.

---

# 2. Architectural Principles

The final FounderOS system must preserve these principles.

## 2.1 Retrieval is source-aware

Use the correct system for the question:

```text
Qdrant  → semantic/lexical text retrieval
Neo4j   → entities / relationships / graph context
XBRL    → precise financial facts
News    → external events
```

Do not turn structured financial facts into ordinary text embeddings.

## 2.2 Evidence-first generation

The answer generator must only reason over an explicit evidence package.

Every material answer claim must be traceable to one or more evidence items.

## 2.3 Temporal awareness

Time must be a first-class field.

The system must support:

```text
before
after
between periods
quarter-to-quarter
year-over-year
latest available
change over time
```

Do not compare facts from different periods without preserving the period.

## 2.4 Contradiction awareness

The system must be able to detect:

```text
Source A: "Demand is accelerating."

Source B: "Demand remains uncertain."
```

as conflicting evidence rather than merging both statements into one unsupported conclusion.

## 2.5 No unsupported inference

The model must distinguish:

```text
FACT
SOURCE CLAIM
MODEL INFERENCE
UNCERTAINTY
```

Suggested output metadata:

```json
{
  "claim_type": "source_claim",
  "confidence": 0.87,
  "evidence_ids": ["..."]
}
```

## 2.6 Reproducibility

A response should be reproducible using:

```text
query
retrieval configuration
model identifier
prompt version
application commit
dataset/evaluation version
```

## 2.7 Observability is part of the product

Every agent execution must be traceable.

At minimum capture:

```text
request_id
session_id
query
route
retrievers used
retrieval latency
LLM latency
token usage
model
prompt version
evidence IDs
final answer
evaluation scores
errors
```

---

# 3. Final Architecture

The target system is:

```text
                              FounderOS
                                  │
                                  ▼
                              API/UI Query
                                  │
                                  ▼
                          Query Understanding
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
                 Semantic      Graph          Fact
                 Retrieval    Retrieval     Retrieval
                    │             │             │
                  Qdrant        Neo4j          XBRL
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                                  ▼
                            Evidence Fusion
                                  │
                                  ▼
                              Reranking
                                  │
                                  ▼
                            Sufficiency Check
                                  │
                         ┌────────┴────────┐
                         │                 │
                      enough            not enough
                         │                 │
                         │                 ▼
                         │          Corrective Retrieval
                         │                 │
                         └────────┬────────┘
                                  ▼
                         Temporal Reasoning
                                  │
                                  ▼
                       Contradiction Detection
                                  │
                                  ▼
                         Answer Synthesis
                                  │
                                  ▼
                     Claims + Citations + Evidence
                                  │
                                  ▼
                             LangGraph
                                  │
                     ┌────────────┼────────────┐
                     ▼            ▼            ▼
                 Persistence   Observability   Feedback
                     │            │            │
                     ▼            ▼            ▼
                  Postgres     Langfuse       User
                                  │
                                  ▼
                              Evaluation
                                  │
                                  ▼
                          FastAPI + Frontend
```

---

# 4. Step 11 — LangGraph Agentic Orchestrator

## Objective

Turn the existing unified retriever into a real stateful agent workflow.

LangGraph should orchestrate the process rather than directly containing all business logic.

Target graph:

```text
START
  │
  ▼
analyze_query
  │
  ▼
plan_retrieval
  │
  ├──────────────┬──────────────┬──────────────┐
  ▼              ▼              ▼
qdrant_search  graph_search   xbrl_search
  │              │              │
  └──────────────┼──────────────┘
                 ▼
          normalize_evidence
                 │
                 ▼
           grade_evidence
                 │
          ┌──────┴──────┐
          │             │
       sufficient?      no
          │             │
         yes            ▼
          │       corrective_retrieval
          │             │
          │             ▼
          └──────► temporal_reasoning
                         │
                         ▼
                 contradiction_check
                         │
                         ▼
                    synthesize
                         │
                         ▼
                       END
```

## New files

```text
src/founder/agent/
├── __init__.py
├── state.py
├── nodes.py
├── routing.py
├── graph.py
├── tools.py
├── prompts.py
└── runner.py
```

## State contract

Create a typed state object containing at least:

```python
class FounderState(TypedDict):
    query: str
    query_plan: dict
    evidence: list
    retrieval_runs: list
    temporal_context: dict
    contradictions: list
    sufficiency: dict
    answer: str | None
    citations: list
    errors: list
    trace_id: str | None
```

## Requirements

The graph must:

- use typed state
- isolate retrieval tools from orchestration
- allow branches
- preserve intermediate evidence
- support retry/error paths
- expose final structured result
- make future checkpointing possible
- avoid putting database calls directly inside prompt code

## Acceptance criteria

The agent must successfully execute:

```text
"What did Microsoft say about AI monetization?"
```

and return:

```json
{
  "answer": "...",
  "evidence": [...],
  "citations": [...],
  "retrieval_plan": {...}
}
```

## Developer verification

```powershell
python -m pytest -q
python -m founder.agent.runner
```

Manual queries:

```text
What did Microsoft say about AI monetization?
What was Microsoft's revenue in fiscal 2025?
Which companies does Microsoft compete with?
What changed in Microsoft's AI strategy between 2025 and 2026?
```

---

# 5. Step 12 — Retrieval Planner + Specialized Tools

## Objective

Convert query analysis into explicit executable retrieval plans.

Example:

```json
{
  "intent": "strategic_temporal",
  "ticker": "MSFT",
  "sources": [
    "qdrant",
    "neo4j",
    "xbrl"
  ],
  "needs_temporal_comparison": true,
  "needs_external_events": false
}
```

## Tools

Create:

```text
src/founder/agent/tools/
├── __init__.py
├── vector_tool.py
├── graph_tool.py
├── fact_tool.py
├── news_tool.py
└── timeline_tool.py
```

Each tool must expose:

```python
ToolResult(
    success=True,
    evidence=[...],
    metadata={...},
    latency_ms=...
)
```

## Requirements

The planner must distinguish:

### Factual question

```text
What was revenue in FY2025?
```

Primary:

```text
XBRL
```

### Semantic question

```text
What did management say about AI monetization?
```

Primary:

```text
Qdrant
```

### Relationship question

```text
Who does Microsoft compete with?
```

Primary:

```text
Neo4j
```

### Temporal question

```text
What changed between Q2 and Q4?
```

Primary:

```text
Qdrant + Neo4j + temporal retrieval
```

### Strategic question

```text
What risks could AI infrastructure spending create?
```

Primary:

```text
Qdrant + Neo4j + XBRL + optionally News
```

## Acceptance criteria

The plan is deterministic for known query patterns and returns the selected tools before execution.

## Developer verification

```powershell
python -m pytest -q
python -m founder.agent.runner
```

Inspect:

```text
retrieval_plan
```

for each test question.

---

# 6. Step 13 — Better GraphRAG + Temporal Knowledge Graph

## Objective

Harden the current Neo4j prototype into a provenance-preserving temporal graph.

Target model:

```text
(:Company)
   │
   └─[:INVESTS_IN]->(:Technology)
                    │
                    └─[:SUPPORTED_BY]->(:Chunk)
                                         │
                                         └─[:PART_OF]->(:Document)
```

For every relationship/event store:

```text
source
published_at
valid_from
valid_to
chunk_id
document_id
evidence
confidence
ticker
```

## Important change

Do not rely only on properties attached to relationships.

Create explicit evidence provenance.

## New/modified graph schema

```text
Company
Person
Product
Technology
Event
Market
Metric
Chunk
Document
```

Relationships:

```text
EXECUTIVE_OF
FOUNDED
ACQUIRED
COMPETES_WITH
PARTNERS_WITH
INVESTS_IN
USES
BUILDS
OFFERS
LAUNCHED
ANNOUNCED
AFFECTS
DRIVES
MENTIONS
GUIDANCE_CHANGE
SUPPORTED_BY
PART_OF
```

## Temporal queries

Implement helpers:

```python
get_company_timeline(...)
get_relationship_timeline(...)
compare_periods(...)
find_new_relationships(...)
find_removed_relationships(...)
```

## Required query patterns

```text
What changed in Microsoft's AI strategy between Q2 2025 and Q1 2026?

What relationships involving Datadog appeared after 2025-01-01?

Which competitors were mentioned across the last four earnings calls?
```

## Acceptance criteria

A relationship can be traced:

```text
entity
→ relationship
→ evidence chunk
→ source document
→ publication date
```

## Developer verification

```powershell
python -m pytest -q
python -m founder.graph.timeline_test
```

Neo4j Browser queries:

```cypher
MATCH (c:Company)-[r]->(x)
RETURN c, r, x
LIMIT 100
```

and:

```cypher
MATCH (c:Company)-[r]->(x)
WHERE r.chunk_id IS NOT NULL
RETURN c.name, type(r), x.name,
       r.chunk_id, r.evidence,
       r.published_at
LIMIT 50
```

---

# 7. Step 14 — Reranking Layer

## Objective

Improve retrieval precision after broad hybrid retrieval.

Pipeline:

```text
Qdrant dense + sparse
        │
        ▼
  20–50 candidates
        │
        ▼
    reranker
        │
        ▼
   top 5–10 evidence
```

Qdrant's current documentation explicitly supports hybrid retrieval followed by reranking with more expressive models. See the official Qdrant hybrid reranking documentation.

## Requirements

Do not rerank the entire corpus.

Implement:

```text
candidate retrieval
→ reranker
→ final retrieval ordering
```

Candidate size should be configurable:

```python
RERANK_CANDIDATES = 30
FINAL_TOP_K = 8
```

## Create

```text
src/founder/retrieval/reranker.py
```

Provide an interface:

```python
class Reranker:
    def rerank(
        self,
        query: str,
        documents: list[Evidence],
        top_k: int
    ) -> list[Evidence]:
        ...
```

## Configurability

The model must come from environment/configuration.

Do not hard-code a model name that may not be available in the user's environment.

Example:

```text
RERANKER_ENABLED=true
RERANKER_MODEL=<configured-model>
```

## Acceptance criteria

Measure:

```text
Recall@5
Recall@10
MRR@10
```

on the retrieval evaluation dataset before and after reranking.

## Developer verification

```powershell
python -m pytest -q
python -m founder.evaluation.evaluate_retrieval
```

---

# 8. Step 15 — Temporal Reasoning Engine

## Objective

Create a dedicated module for comparing evidence across periods.

Create:

```text
src/founder/reasoning/
├── __init__.py
├── temporal.py
├── comparisons.py
├── claims.py
└── dates.py
```

## Input

A set of evidence records with:

```text
ticker
published_at
year
quarter
document_type
source
text
```

## Output

Structured comparison:

```json
{
  "topic": "AI monetization",
  "period_a": "2025-Q2",
  "period_b": "2026-Q1",
  "changes": [
    {
      "dimension": "monetization",
      "before": "...",
      "after": "...",
      "evidence_ids": ["...", "..."]
    }
  ]
}
```

## Required functions

```python
normalize_period(...)
group_by_period(...)
compare_periods(...)
detect_change(...)
build_change_summary(...)
```

## Rules

- never compare unsorted dates
- never assume publication date equals fiscal period
- prefer fiscal year/quarter metadata where available
- preserve exact source dates
- label inferred chronology as inference
- never claim a causal relationship from temporal ordering alone

## Acceptance criteria

Test:

```text
What changed in Microsoft's AI strategy between 2025 and 2026?
```

and confirm the output separates:

```text
Period A
Period B
Change
Evidence
```

## Developer verification

```powershell
python -m pytest -q
python -m founder.reasoning.temporal_test
```

---

# 9. Step 16 — Contradiction Detection

## Objective

Detect conflicting statements instead of hiding them.

Pipeline:

```text
retrieved evidence
      ↓
claim extraction
      ↓
claim grouping
      ↓
pairwise conflict detection
      ↓
contradiction report
```

Create:

```text
src/founder/reasoning/contradictions.py
```

## Contradiction object

```json
{
  "claim_a": "...",
  "claim_b": "...",
  "type": "direct_conflict",
  "evidence_a": ["..."],
  "evidence_b": ["..."],
  "time_relation": "later",
  "severity": "medium"
}
```

## Types

```text
direct_conflict
change_over_time
scope_difference
metric_definition_difference
apparent_conflict
```

## Important distinction

The system must not call something a contradiction merely because:

```text
Q2: growth was 20%
Q4: growth was 12%
```

That could simply be a change over time.

A contradiction is about incompatible claims in relevant context.

## Acceptance criteria

For conflicting source examples, the system surfaces both statements.

## Developer verification

```powershell
python -m pytest -q
python -m founder.reasoning.contradiction_test
```

---

# 10. Step 17 — Evidence Sufficiency + Corrective Retrieval

## Objective

Introduce the "agent loop".

Current:

```text
retrieve once
→ answer
```

Target:

```text
retrieve
→ grade evidence
→ insufficient?
→ broaden/reformulate
→ retrieve again
→ grade
→ answer
```

Create:

```text
src/founder/agent/
├── sufficiency.py
├── corrective.py
└── query_rewriter.py
```

## Sufficiency signals

Evaluate:

```text
coverage
source diversity
temporal coverage
entity coverage
directness
contradiction state
```

Example:

```json
{
  "sufficient": false,
  "reason": [
    "Only one reporting period found",
    "No supporting SEC evidence",
    "Question asks for external cause"
  ],
  "missing": [
    "prior_period",
    "external_event"
  ]
}
```

## Corrective strategies

Implement:

```text
query expansion
ticker expansion
period expansion
source expansion
graph expansion
fact fallback
```

## Hard limit

Prevent loops:

```python
MAX_RETRIEVAL_ROUNDS = 2
```

The agent must terminate even if evidence remains incomplete.

## Acceptance criteria

The agent can say:

```text
"I don't have enough evidence to establish the cause."
```

instead of hallucinating.

## Developer verification

```powershell
python -m pytest -q
python -m founder.agent.corrective_test
```

---

# 11. Step 18 — Answer Synthesis + Citation Engine

## Objective

Generate final answers from a structured evidence package.

Create:

```text
src/founder/generation/
├── __init__.py
├── answer.py
├── citations.py
├── prompts.py
└── schemas.py
```

## Answer contract

The answer should contain:

```json
{
  "answer": "...",
  "claims": [
    {
      "text": "...",
      "evidence_ids": ["..."],
      "claim_type": "fact|source_claim|inference",
      "confidence": 0.84
    }
  ],
  "citations": [
    {
      "evidence_id": "...",
      "citation_text": "...",
      "source": "SEC",
      "date": "..."
    }
  ],
  "limitations": []
}
```

## Generation rules

The answer generator must:

- never cite evidence not actually retrieved
- never invent URLs
- never fabricate dates
- never merge unrelated companies
- distinguish management statements from externally verified facts
- distinguish numerical facts from narrative claims
- explicitly mention uncertainty when evidence is insufficient

## Citation format

For the UI/API, use stable citation IDs.

Example:

```text
[1]
[2]
[3]
```

Internally map them to:

```text
chunk_id
document_id
source
published_at
url/accession
```

## Developer verification

```powershell
python -m pytest -q
python -m founder.generation.answer_test
```

Manual:

```powershell
python -m founder.agent.runner
```

---

# 12. Step 19 — Langfuse Observability

## Objective

Instrument the full application.

Langfuse currently supports tracing, evaluations, datasets, experiments and production feedback workflows. Use it as the central observability/evaluation surface.

## Create

```text
src/founder/observability/
├── __init__.py
├── langfuse.py
├── tracing.py
└── context.py
```

## Trace structure

Every query should produce something conceptually like:

```text
Trace
│
├── query_analyzer
├── retrieval_planner
│
├── qdrant_search
│   ├── dense
│   ├── sparse
│   └── reranker
│
├── neo4j_search
├── xbrl_search
│
├── sufficiency_check
├── corrective_retrieval
├── temporal_reasoning
├── contradiction_check
└── answer_generation
```

## Record

At minimum:

```text
trace_id
session_id
query
model
latency
token usage
retrieval count
evidence IDs
error
final answer
```

## Environment

Use configuration such as:

```text
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=
LANGFUSE_ENABLED=true
```

Do not hard-code secrets.

## Acceptance criteria

A single query produces a complete trace.

## Developer verification

```powershell
python -m pytest -q
python -m founder.observability.test_trace
```

Then inspect the trace in Langfuse.

---

# 13. Step 20 — Evaluation Framework

## Objective

Make quality measurable.

Evaluation categories:

```text
retrieval
grounding
faithfulness
citation correctness
temporal correctness
structured-fact correctness
graph correctness
latency
cost
```

Ragas can be used for RAG evaluation metrics such as faithfulness, while Langfuse can host datasets/experiments and compare application versions.

## Create

```text
src/founder/evaluation/
├── __init__.py
├── dataset.py
├── retrieval_eval.py
├── answer_eval.py
├── factual_eval.py
├── temporal_eval.py
├── graph_eval.py
└── run_experiment.py
```

## Evaluation dataset

Expand:

```text
data/05_evaluation/
```

into:

```text
data/05_evaluation/
├── retrieval_questions.json
├── answer_questions.json
├── temporal_questions.json
├── graph_questions.json
└── fact_questions.json
```

Minimum dataset target:

```text
20 factual
20 semantic
20 temporal
20 graph
20 strategic
```

Total:

```text
100 test cases
```

## Retrieval metrics

Measure:

```text
Recall@5
Recall@10
MRR@10
NDCG@10
```

## Answer metrics

Measure:

```text
faithfulness
citation coverage
citation precision
answer correctness
```

## Strategic-query rubric

Score separately:

```text
evidence coverage
cross-source synthesis
temporal correctness
uncertainty handling
contradiction handling
```

## Acceptance criteria

Create a baseline report:

```text
docs/evaluation/Baseline.md
```

containing:

```text
dataset version
code version
model versions
retrieval metrics
answer metrics
latency
known failures
```

## Developer verification

```powershell
python -m pytest -q
python -m founder.evaluation.run_experiment
```

---

# 14. Step 21 — Structured Fact Resolution / Numerical Accuracy

## Objective

Make XBRL retrieval production-grade.

The current facts layer is intentionally simple. Harden it now.

## Problems to solve

Handle:

```text
duplicate facts
alternative concepts
units
instant vs duration facts
fiscal period ambiguity
annual vs quarterly facts
restatements
latest filing
multiple frames
```

## Create

```text
src/founder/retrieval/fact_resolution.py
```

Functions:

```python
resolve_concept(...)
resolve_period(...)
resolve_latest(...)
resolve_duplicate(...)
normalize_unit(...)
format_financial_value(...)
```

## Example

For:

```text
What was Microsoft's revenue in FY2025?
```

return:

```json
{
  "ticker": "MSFT",
  "metric": "Revenue",
  "period": "FY2025",
  "value": 281724000000,
  "unit": "USD",
  "source": "XBRL",
  "filing": "10-K",
  "filed": "...",
  "accession": "..."
}
```

## Guardrails

The system must not compare:

```text
quarterly revenue
```

against:

```text
annual revenue
```

without explicitly normalizing the periods.

## Developer verification

```powershell
python -m pytest -q
python -m founder.retrieval.fact_resolution_test
```

---

# 15. Step 22 — Query/Answer API with FastAPI

## Objective

Expose FounderOS through a clean backend API.

FastAPI's current testing workflow uses `TestClient`/HTTPX with pytest.

## Create

```text
src/founder/api/
├── __init__.py
├── main.py
├── schemas.py
├── dependencies.py
└── routes/
    ├── __init__.py
    ├── query.py
    ├── health.py
    └── feedback.py
```

## Endpoints

### Health

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "qdrant": "ok",
  "neo4j": "ok",
  "langfuse": "ok"
}
```

### Query

```http
POST /api/v1/query
```

Request:

```json
{
  "query": "What changed in Microsoft's AI monetization narrative?",
  "top_k": 8
}
```

Response:

```json
{
  "answer": "...",
  "claims": [...],
  "citations": [...],
  "retrieval_plan": {...},
  "trace_id": "...",
  "latency_ms": 1234
}
```

### Feedback

```http
POST /api/v1/feedback
```

Store:

```text
trace_id
rating
comment
```

## Testing

Create:

```text
tests/api/
```

## Developer verification

```powershell
python -m pytest -q
uvicorn founder.api.main:app --reload
```

Then:

```text
http://127.0.0.1:8000/docs
```

Test the `/health` and `/api/v1/query` endpoints.

---

# 16. Step 23 — Frontend / Founder Intelligence Console

## Objective

Create a small but polished UI rather than a generic chat box.

Recommended layout:

```text
┌───────────────────────────────────────────────────────────┐
│ FounderOS                                  ● System Ready │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ Ask a strategic question...                               │
│                                                           │
│ [ What changed in Microsoft's AI strategy? ] [Ask]        │
│                                                           │
├────────────────────────────┬──────────────────────────────┤
│ Answer                     │ Evidence                     │
│                            │                              │
│ concise answer             │ SEC      Q4 2025             │
│                            │ Earnings  Q1 2026             │
│ [1] [2] [3]                │ News     ...                 │
│                            │                              │
├────────────────────────────┴──────────────────────────────┤
│ Timeline                                                   │
│ 2025 Q2 ───── 2025 Q4 ───── 2026 Q1                      │
│      statement      change       latest statement          │
└───────────────────────────────────────────────────────────┘
```

## UI features

Implement:

```text
query
answer
citations
evidence cards
source filters
ticker filter
date range
timeline
graph relationships
confidence/uncertainty indicator
feedback
```

## Important

Do not display a meaningless single "confidence score" for the whole answer.

Instead show evidence-aware labels such as:

```text
Supported by 4 sources
2 reporting periods
1 conflicting statement detected
```

## Developer verification

Run frontend and backend separately and confirm:

```text
query
→ API
→ agent
→ evidence
→ answer
→ citations
```

---

# 17. Step 24 — Streaming + Agent Trace UI

## Objective

Show what FounderOS is doing without exposing hidden chain-of-thought.

Display only safe execution metadata:

```text
Analyzing query...
Searching financial filings...
Searching earnings calls...
Checking graph relationships...
Checking prior periods...
Verifying evidence...
Generating answer...
```

Do NOT expose hidden reasoning or chain-of-thought.

## API

Implement a streaming endpoint, e.g.:

```http
POST /api/v1/query/stream
```

Use server-sent events or another simple streaming mechanism.

Events:

```json
{
  "type": "status",
  "message": "Searching SEC filings"
}
```

```json
{
  "type": "evidence",
  "evidence_id": "...",
  "source": "SEC"
}
```

```json
{
  "type": "answer_token",
  "text": "..."
}
```

---

# 18. Step 25 — Production Persistence / Checkpointing

## Objective

Persist important agent/session state.

Use a durable state store for:

```text
session
thread
query
agent state
feedback
```

Do not rely on Python process memory.

## Suggested components

```text
PostgreSQL
    │
    ├── sessions
    ├── feedback
    ├── query_history
    └── agent_runs
```

Use LangGraph persistence/checkpointing for the graph state.

## Create

```text
src/founder/storage/
├── __init__.py
├── postgres.py
├── models.py
└── repositories.py
```

## Acceptance criteria

Restart the API process and verify that session-level state can still be recovered.

---

# 19. Step 26 — Security + Configuration Hardening

## Objective

Make the application safe to put on GitHub and run outside localhost.

## Requirements

Move all secrets/config into environment variables:

```text
OPENAI_API_KEY
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
QDRANT_URL

LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY
LANGFUSE_HOST
LANGFUSE_ENABLED

RERANKER_ENABLED
RERANKER_MODEL

APP_ENV
LOG_LEVEL
```

Never commit:

```text
.env
API keys
database passwords
tokens
private certificates
```

## Add

```text
.env.example
```

with placeholders.

## Validate

Create startup configuration validation:

```python
validate_settings()
```

It should fail fast for required production settings.

---

# 20. Step 27 — Automated Testing / Quality Gates

## Objective

Make every pull request testable.

Project test structure:

```text
tests/
├── ingestion/
├── retrieval/
├── graph/
├── agent/
├── reasoning/
├── generation/
├── evaluation/
└── api/
```

Test levels:

```text
unit
integration
retrieval regression
agent regression
API
```

## Minimum unit tests

Test:

```text
query classification
ticker extraction
period parsing
fact resolution
citation mapping
graph query formatting
evidence deduplication
contradiction detection
```

## Integration tests

Use:

```text
Qdrant
Neo4j
```

in CI/test services or controlled local containers.

## Acceptance gate

```powershell
python -m pytest -q
```

must pass before merge.

---

# 21. Step 28 — Dockerize the Application

## Objective

Create a reproducible local/prod-ish environment.

Final compose structure:

```text
docker-compose.yml
```

Services:

```text
qdrant
neo4j
postgres
api
frontend
```

Optional:

```text
worker
```

## Requirements

- health checks
- named volumes
- environment configuration
- service dependencies
- restart policies
- no secrets inside compose file
- persistent Qdrant volume
- persistent Neo4j volume
- persistent Postgres volume

## Developer verification

```powershell
docker compose down
docker compose up -d --build
docker compose ps
```

Then:

```powershell
curl http://localhost:8000/health
```

---

# 22. Step 29 — CI/CD with GitHub Actions

## Objective

Every push should run the quality pipeline.

Create:

```text
.github/
└── workflows/
    ├── test.yml
    └── build.yml
```

## Test workflow

Should:

```text
checkout
→ setup Python
→ install dependencies
→ lint
→ unit tests
→ integration tests where practical
```

## Build workflow

Should:

```text
docker build
```

for backend.

Do not publish secrets.

## Acceptance criteria

A clean GitHub Actions run appears on the repository.

---

# 23. Step 30 — Data/Index Rebuild Pipeline

## Objective

Make ingestion and re-indexing reproducible.

Create:

```text
scripts/
├── rebuild_dataset.py
├── rebuild_qdrant.py
├── rebuild_graph.py
├── run_evals.py
└── bootstrap.py
```

Pipeline:

```text
raw data
→ primary data
→ chunks
→ Qdrant
→ Neo4j
→ evaluation
```

The command should be deterministic for the same source version/config where practical.

## Acceptance criteria

A new machine can run a documented bootstrap sequence.

---

# 24. Step 31 — External Event / News Quality Hardening

## Objective

Make the news layer useful for causal-context research without making unsupported causal claims.

The system must preserve:

```text
title
url
domain
published_at
ticker
source metadata
```

If publisher article text is not licensed/permitted for local ingestion, do not silently scrape and redistribute it.

## Add event extraction

Create:

```text
src/founder/news/
├── __init__.py
├── events.py
├── event_resolution.py
└── timeline.py
```

Event categories:

```text
product_launch
acquisition
regulation
pricing_change
leadership_change
partnership
security_incident
market_event
macro_event
guidance_change
```

## Acceptance criteria

FounderOS can return:

```text
External events around the date of a guidance change
```

with evidence and dates.

---

# 25. Step 32 — Evidence Pack / Export

## Objective

Allow a founder to export an investigation.

Create an export object:

```json
{
  "question": "...",
  "answer": "...",
  "claims": [...],
  "timeline": [...],
  "graph_findings": [...],
  "financial_facts": [...],
  "sources": [...],
  "limitations": [...],
  "trace_id": "..."
}
```

Support:

```text
JSON
Markdown
HTML
```

Optional later:

```text
PDF
```

## Example

```powershell
python -m founder.export investigation \
  --query "What changed in Microsoft's AI strategy?"
```

Output:

```text
artifacts/investigation_<timestamp>.md
```

---

# 26. Step 33 — Founder Workflow Features

## Objective

Turn the technology into an actual founder-oriented product.

Add workflows such as:

### Company brief

```text
/company MSFT
```

Generates:

```text
business
financial trajectory
AI strategy
competitors
recent events
management commentary
risks
open questions
```

### Competitive comparison

```text
/compare CRM NOW
```

Generates a source-backed comparison across:

```text
AI strategy
pricing
growth
margins
products
management commentary
competitive mentions
```

### Change monitor

```text
/changes MSFT
```

Shows:

```text
new claims
changed guidance
new products
new partnerships
new competitors
new risks
```

### Investment / strategy brief

```text
/brief DDOG
```

Produces:

```text
current narrative
financial signals
strategic shifts
external events
contradictions
questions worth investigating
```

These are product features, not additional retrieval databases.

---

# 27. Step 34 — Final Evaluation / Regression Baseline

## Objective

Freeze a release baseline.

Create:

```text
docs/evaluation/
├── BASELINE.md
├── RETRIEVAL.md
├── AGENT.md
├── TEMPORAL.md
└── KNOWN_FAILURES.md
```

Record:

```text
commit
dataset version
embedding model
reranker
LLM/model
prompt versions
Qdrant config
Neo4j version
evaluation dataset version
```

Metrics:

```text
Recall@5
Recall@10
MRR
NDCG
Faithfulness
Citation precision
Citation coverage
Temporal accuracy
Fact accuracy
Latency p50
Latency p95
Token cost
```

## Acceptance criteria

Create one reproducible baseline command:

```powershell
python -m founder.evaluation.run_release_baseline
```

---

# 28. Step 35 — Documentation / Architecture / Demo

## Objective

Make the repository explainable to a hiring manager.

Create:

```text
README.md
docs/
├── architecture.md
├── data_model.md
├── retrieval.md
├── agent.md
├── evaluation.md
├── deployment.md
├── limitations.md
└── specs/
```

## README must clearly explain

### Problem

FounderOS answers strategic questions that span:

```text
filings
earnings calls
financial facts
graph relationships
external events
multiple reporting periods
```

### Architecture

Show:

```text
Qdrant
Neo4j
XBRL
LangGraph
Langfuse
FastAPI
Frontend
```

### Why hybrid?

Explain why one retrieval method is insufficient.

### Why graph?

Explain relationship and temporal context.

### Why XBRL?

Explain numeric correctness.

### Why agents?

Explain adaptive retrieval and corrective retrieval.

### Why evaluation?

Explain measurable quality and regression control.

---

# 29. Step 36 — Final Demo Scenarios

The final demo should showcase scenarios that reveal the architecture.

## Scenario 1 — Semantic

```text
What did management say about AI monetization?
```

Demonstrates:

```text
Qdrant
earnings/SEC evidence
citation
```

## Scenario 2 — Financial fact

```text
What was Microsoft's revenue in FY2025?
```

Demonstrates:

```text
XBRL
period resolution
fact citation
```

## Scenario 3 — Graph

```text
Who are Microsoft's major competitors mentioned in the corpus?
```

Demonstrates:

```text
Neo4j
relationship retrieval
evidence provenance
```

## Scenario 4 — Temporal

```text
What changed in Microsoft's AI strategy between Q2 2025 and Q1 2026?
```

Demonstrates:

```text
multi-period retrieval
timeline
graph
Qdrant
```

## Scenario 5 — Strategic

```text
Is there evidence that AI infrastructure investment is becoming a margin risk?
```

Demonstrates:

```text
Qdrant
Neo4j
XBRL
temporal reasoning
contradiction handling
uncertainty
```

Do not present speculative conclusions as facts.

The system should explicitly separate:

```text
Evidence
Observed change
Possible explanation
Unverified inference
```

---

# 30. Recommended Final Repository Structure

By the end, target:

```text
FounderOS/
│
├── data/
│   ├── 01_raw/
│   ├── 03_primary/
│   ├── 04_chunks/
│   └── 05_evaluation/
│
├── src/
│   └── founder/
│       ├── ingestion/
│       ├── retrieval/
│       ├── graph/
│       ├── agent/
│       │   └── tools/
│       ├── reasoning/
│       ├── generation/
│       ├── observability/
│       ├── evaluation/
│       ├── storage/
│       ├── news/
│       ├── api/
│       └── export/
│
├── tests/
│   ├── ingestion/
│   ├── retrieval/
│   ├── graph/
│   ├── agent/
│   ├── reasoning/
│   ├── generation/
│   ├── evaluation/
│   └── api/
│
├── frontend/
│
├── docs/
│   ├── specs/
│   ├── evaluation/
│   ├── architecture.md
│   ├── data_model.md
│   ├── retrieval.md
│   ├── agent.md
│   ├── deployment.md
│   └── limitations.md
│
├── scripts/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

# 31. Exact Developer Execution Commands

These are the commands the developer should run **after each successful Copilot step**.

## After Step 11

```powershell
python -m pytest -q
python -m founder.agent.runner
```

## After Step 12

```powershell
python -m pytest -q
python -m founder.agent.runner
```

## After Step 13

```powershell
python -m pytest -q
python -m founder.graph.timeline_test
```

## After Step 14

```powershell
python -m pytest -q
python -m founder.evaluation.evaluate_retrieval
```

## After Step 15

```powershell
python -m pytest -q
python -m founder.reasoning.temporal_test
```

## After Step 16

```powershell
python -m pytest -q
python -m founder.reasoning.contradiction_test
```

## After Step 17

```powershell
python -m pytest -q
python -m founder.agent.corrective_test
```

## After Step 18

```powershell
python -m pytest -q
python -m founder.generation.answer_test
```

## After Step 19

```powershell
python -m pytest -q
python -m founder.observability.test_trace
```

## After Step 20

```powershell
python -m pytest -q
python -m founder.evaluation.run_experiment
```

## After Step 21

```powershell
python -m pytest -q
python -m founder.retrieval.fact_resolution_test
```

## After Step 22

```powershell
python -m pytest -q
uvicorn founder.api.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## After Step 23

Run backend:

```powershell
uvicorn founder.api.main:app --reload
```

Run frontend using the frontend project's documented command.

## After Step 24

```powershell
python -m pytest -q
```

Then test:

```text
POST /api/v1/query/stream
```

## After Step 25

```powershell
python -m pytest -q
docker compose up -d
```

## After Step 26

```powershell
python -m pytest -q
```

Also verify:

```text
.env
```

is not tracked:

```powershell
git status --short
```

## After Step 27

```powershell
python -m pytest -q
```

## After Step 28

```powershell
docker compose down
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
```

## After Step 29

Push to a branch and verify GitHub Actions.

## After Step 30

```powershell
python -m founder.pipeline.rebuild_dataset
python -m founder.evaluation.run_experiment
```

## After Step 31

```powershell
python -m pytest -q
```

## After Step 32

```powershell
python -m pytest -q
python -m founder.export investigation --query "What changed in Microsoft's AI strategy?"
```

## After Step 33

```powershell
python -m pytest -q
```

Then run the founder workflow examples.

## After Step 34

```powershell
python -m founder.evaluation.run_release_baseline
```

## After Step 35

```powershell
python -m pytest -q
```

## After Step 36

Run the five demo scenarios manually and capture screenshots/results for the README/demo.

---

# 32. Global Acceptance Checklist

Before calling FounderOS complete, all of these must be true.

## Data

- [ ] SEC filings available
- [ ] XBRL facts available
- [ ] earnings calls available
- [ ] news metadata available
- [ ] source-aware chunks available
- [ ] data validation passes

## Retrieval

- [ ] dense retrieval works
- [ ] sparse retrieval works
- [ ] hybrid retrieval works
- [ ] reranking works
- [ ] metadata filtering works
- [ ] graph retrieval works
- [ ] XBRL fact retrieval works

## Agent

- [ ] query analysis works
- [ ] retrieval planning works
- [ ] multi-tool execution works
- [ ] sufficiency checking works
- [ ] corrective retrieval works
- [ ] temporal reasoning works
- [ ] contradiction detection works
- [ ] answer synthesis works

## Grounding

- [ ] evidence IDs are stable
- [ ] citations map to evidence
- [ ] unsupported claims are rejected or labeled
- [ ] conflicting evidence is surfaced
- [ ] financial periods are preserved

## Observability

- [ ] traces are available
- [ ] latency is captured
- [ ] token usage is captured
- [ ] retrieval behavior is inspectable
- [ ] evaluations are stored

## Evaluation

- [ ] retrieval metrics exist
- [ ] answer metrics exist
- [ ] temporal tests exist
- [ ] fact tests exist
- [ ] graph tests exist
- [ ] baseline is reproducible

## API/UI

- [ ] health endpoint works
- [ ] query endpoint works
- [ ] streaming works
- [ ] citations display
- [ ] evidence displays
- [ ] timeline displays
- [ ] feedback works

## Engineering

- [ ] unit tests pass
- [ ] integration tests pass
- [ ] Docker works
- [ ] GitHub Actions works
- [ ] secrets are excluded
- [ ] `.env.example` exists
- [ ] README is complete

---

# 33. Definition of Done

FounderOS is complete when a new developer can clone the repository and understand this flow:

```text
Question
   ↓
Query analysis
   ↓
Retrieval plan
   ↓
Qdrant + Neo4j + XBRL (+ News)
   ↓
Reranking
   ↓
Evidence sufficiency
   ↓
Corrective retrieval if necessary
   ↓
Temporal reasoning
   ↓
Contradiction detection
   ↓
Evidence-backed synthesis
   ↓
Citations
   ↓
Langfuse trace
   ↓
Evaluation
   ↓
API/UI response
```

And a user can ask a query such as:

```text
What changed in Microsoft's AI monetization narrative between Q2 2025 and Q1 2026?
```

and FounderOS can produce:

```text
1. What management said in each period
2. What changed
3. Evidence supporting the change
4. Related graph entities/relationships
5. Relevant financial facts
6. Relevant external events, when available
7. Contradictions or uncertainty
8. Exact citations
```

without relying on unsupported model memory.

---

# 34. Copilot Operating Rule

Use the following instruction whenever giving this plan to GitHub Copilot:

> **Implement only the next incomplete step in `FOUNDEROS_REMAINING_PLAN.md`.**
>
> Before coding, inspect the repository and identify what already exists.
>
> Create `docs/specs/STEP_XX_<name>.md`.
>
> Implement the step fully, including tests and error handling.
>
> Do not rewrite unrelated existing modules.
>
> Do not skip acceptance criteria.
>
> Do not proceed to the next step automatically.
>
> At the end, report:
>
> 1. files created
> 2. files modified
> 3. design decisions
> 4. tests added
> 5. commands the developer should run
> 6. expected verification output
> 7. known limitations
>
> Then stop.

---

# 35. Official Technical References

Use current official documentation while implementing:

- LangGraph: https://docs.langchain.com/oss/python/langgraph
- Neo4j GraphRAG for Python: https://neo4j.com/docs/neo4j-graphrag-python/current/
- Neo4j GraphRAG retrievers: https://neo4j.com/docs/neo4j-graphrag-python/current/api.html
- Qdrant hybrid search: https://qdrant.tech/documentation/search/hybrid-queries/
- Qdrant hybrid + reranking: https://qdrant.tech/documentation/tutorials-basics/reranking-hybrid-search/
- Qdrant filtering: https://qdrant.tech/documentation/search/filtering/
- Langfuse evaluation: https://langfuse.com/docs/evaluation/overview
- Langfuse datasets: https://langfuse.com/docs/evaluation/experiments/datasets
- Langfuse experiments: https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk
- Ragas documentation: https://docs.ragas.io/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- SEC APIs: https://www.sec.gov/edgar/sec-api-documentation

