# FounderOS
An AI decision-intelligence system that connects company filings, earnings calls, market events and news into a temporal knowledge graph, then uses agentic retrieval and evidence verification to answer strategic questions with citations, confidence and contradiction analysis.

## Architecture

FounderOS uses the right source for the question: Qdrant for narrative retrieval, Neo4j for entities and relationships, XBRL for precise financial facts, and dated news metadata for external context. LangGraph coordinates retrieval and bounded corrective loops; the answer layer can cite only retrieved evidence IDs. FastAPI exposes the API and the `frontend/` console displays status, evidence, citations, and timeline context.

## Run locally

From `founder/`, run `python -m pytest -q` after installing `requirements.txt`. Start the API with `uvicorn founder.api.main:app --reload`, then start the console from `frontend/` with `npm install` and `npm run dev`. Qdrant and Neo4j are needed for live retrieval; offline tests and export/workflow utilities do not require those services.

Create an evidence pack with:

```powershell
python -m founder.export investigation --query "What changed in Microsoft's AI strategy?"
python -m founder.evaluation.run_release_baseline
```

## Founder workflows

The workflow layer turns these commands into explicit, traceable queries:

```text
/company MSFT
/compare CRM NOW
/changes MSFT
/brief DDOG
```

## Demo scenarios

1. What did management say about AI monetization? (semantic retrieval and citations)
2. What was Microsoft's revenue in FY2025? (XBRL period resolution)
3. Who are Microsoft's major competitors mentioned in the corpus? (graph retrieval)
4. What changed in Microsoft's AI strategy between Q2 2025 and Q1 2026? (temporal comparison)
5. Is there evidence that AI infrastructure investment is becoming a margin risk? (cross-source uncertainty and contradiction handling)

See `founder/docs/architecture.md`, `founder/docs/limitations.md`, and `founder/docs/evaluation/BASELINE.md` for implementation boundaries and release context.
