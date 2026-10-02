# Step 29 — CI/CD with GitHub Actions

## Goal

Automate testing and building on every push to GitHub.

## Non-goals

- Deployment to cloud (that's Step 32+)
- Secret rotation

## Inputs

- Repository on GitHub
- Tests from Step 27
- Docker images from Step 28

## Outputs

```text
.github/
└── workflows/
    ├── test.yml
    └── build.yml
```

## Test workflow (test.yml)

Triggers: `on: [push, pull_request]`

Jobs:
1. Lint (ruff)
2. Type check (mypy, optional)
3. Unit tests (pytest -m unit)
4. Integration tests (pytest -m integration)

Should not publish secrets or artifacts.

## Build workflow (build.yml)

Triggers: `on: [push]` (only on main branch)

Jobs:
1. Build backend Docker image
2. Build frontend static assets

Do NOT push to registry (local development only).

## Acceptance criteria

- Test workflow passes on clean push
- Build workflow completes without errors
- Coverage report visible in logs

## Files to create

```text
.github/workflows/test.yml
.github/workflows/build.yml
```

## Known limitations

- No artifact storage (GitHub Actions free tier)
- No deployment triggers
- No secret management yet

## Rollback / recovery

Workflows are non-invasive; can be removed without affecting code.
