# Step 27 — Automated Testing / Quality Gates

## Goal

Establish a comprehensive test suite that runs on every commit to ensure code quality.

## Non-goals

- 100% code coverage requirement (target is >70%)
- Complex mocking frameworks (use unittest.mock)

## Inputs

- Existing unit tests from Steps 13-26
- pyproject.toml configuration

## Outputs

```text
pytest.ini
pyproject.toml (updated)
```

## Test structure

```text
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── test_config.py
│   ├── test_metrics.py
│   └── ...
├── integration/
│   ├── test_api.py
│   └── test_storage.py
└── fixtures/
    └── sample_data.py
```

## Test types

**Unit tests** (fast, no services required):
- Configuration
- Metrics calculations
- Period mapping
- Citations
- Claims extraction
- Contradictions detection
- Sufficiency grading

**Integration tests** (slower, may need services):
- API endpoints
- Storage repositories
- Serialization round-trips

## Pytest configuration

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
  unit: unit tests
  integration: integration tests
  slow: slow tests
```

## Acceptance criteria

- `pytest -q` runs all tests
- `pytest -m unit` runs unit tests only
- `pytest --cov=src/founder --cov-report=html` generates coverage report
- Coverage > 70% for all modules
- All tests pass on clean repository

## Files to create/modify

```text
pytest.ini
pyproject.toml (add pytest config and test dependencies)
conftest.py (shared fixtures)
tests/unit/__init__.py
tests/integration/__init__.py
```

## Known limitations

- Integration tests require services running (Qdrant, Neo4j, Postgres)
- Mocking used for external API calls

## Rollback / recovery

Testing is non-invasive; can be removed without affecting application.
