# Step 30 — Data/Index Rebuild Pipeline

## Goal

Make ingestion and re-indexing reproducible so a new machine can bootstrap
the full pipeline from raw data to evaluated system.

## Non-goals

- Automated daily rebuilds (that's Step 32+)
- Cloud data pipelines (that's Step 33+)

## Inputs

- Raw data in `data/01_raw/`
- Existing ingestion modules
- Retrieval indexing
- Graph extraction
- Evaluation framework

## Outputs

```text
scripts/
├── __init__.py
├── bootstrap.py
├── rebuild_dataset.py
├── rebuild_qdrant.py
├── rebuild_graph.py
└── run_evals.py
```

## Pipeline

```
raw data (data/01_raw/)
    ↓
rebuild_dataset.py → primary data (data/03_primary/)
    ↓
chunk_documents.py → chunks (data/04_chunks/)
    ↓
rebuild_qdrant.py → Qdrant indexes
    ↓
rebuild_graph.py → Neo4j graph
    ↓
run_evals.py → evaluation results (data/05_evaluation/)
```

## Bootstrap script

The entry point:

```python
python scripts/bootstrap.py
```

Should:
1. Check for raw data
2. Check for services (Qdrant, Neo4j)
3. Run rebuild pipeline
4. Run evaluation
5. Print summary

## Acceptance criteria

- `python scripts/bootstrap.py` completes without error
- `data/03_primary/` contains `documents.jsonl`, `facts.jsonl`, `earnings.jsonl`, `news.jsonl`
- Qdrant has populated collections
- Neo4j has populated entities and relationships
- Evaluation metrics printed to console

## Known limitations

- Rebuilds require all services running
- No incremental rebuilds (full rebuild each time)
- No distributed processing (single-machine)

## Rollback / recovery

Rebuilds are idempotent; safe to rerun multiple times.
