# Decision Log

Every decision taken in [PLAN.md](PLAN.md). Status: **Proposed** means I chose it and you have not yet confirmed. Tell me which ones to change.

| ID | Decision | Status |
|---|---|---|
| D-01 | One CI workflow, working directory `founder/`, Python 3.12 only | Implemented (Phase 1) |
| D-02 | Split runtime and dev requirements | Implemented (Phase 1) |
| D-03 | Auto-mark tests as `unit`; CI runs the whole suite | Implemented (Phase 1) |
| D-04 | Auto-fix lint, relax rules that don't suit scripts | Implemented (Phase 1) |
| D-05 | Remove committed `node_modules` and `dist` from git | Implemented (Phase 1) |
| D-06 | "Full" means 100 companies | **Needs your confirmation** |
| D-07 | Wire the real agent into the API; delete the mock | Proposed |
| D-08 | POST + fetch streaming instead of EventSource | Proposed |
| D-09 | Drop Postgres from compose | Proposed |
| D-10 | Fit data into free tiers using quantization and pruning | Proposed |
| D-11 | Host: Hugging Face Spaces (API) + Cloudflare Pages (UI) + Qdrant Cloud + Neo4j AuraDB | Proposed |
| D-12 | Bring-your-own OpenAI key, sent per request, never stored | Proposed |
| D-13 | Rate limit, strict CORS, read-only DB credentials | Proposed |

---

### D-01: One CI workflow, working directory `founder/`, Python 3.12 only
- **Why:** The workflows run from the repo root, but the project is in `founder/`. That is the main reason everything fails. Fixing it needs `working-directory`.
- **Why one Python version:** The project was built on 3.13 and pins Kedro 1.6 and scikit-learn 1.8. A 3.10/3.11/3.12 matrix triples run time and adds failures on versions you don't use. I picked 3.12 as the newest version that the pinned libraries and GitHub runners support well.
- **Rejected:** Keep the 3.10–3.12 matrix (cost and breakage with no benefit for an app, as opposed to a library). Move the project to the repo root (large, risky file moves).

### D-02: Split runtime and dev requirements
- **Why:** `requirements.txt` is missing the packages the API needs (fastapi, uvicorn, pydantic-settings), so tests and Docker both break. It also contains Jupyter, Kedro-Viz and notebook, which make the Docker image huge and aren't needed to serve queries.
- **Rejected:** One file for everything (large image, slower CI). Switch to Poetry or uv now (extra change with no fix for the current failure).

### D-03: Auto-mark tests as `unit`; CI runs the whole suite
- **Why:** The workflow runs `pytest -m unit`, but nearly no test has that marker, so pytest finds 0 tests and exits with a failure. Marking by `conftest.py` rule (tests that need Qdrant, Neo4j or network are `integration`) fixes it without editing 100+ tests by hand. **Changed during implementation:** the one `integration` test only uses FastAPI's TestClient on `/health` and needs no live service, so CI just runs the whole suite (114 tests, about 10s) instead of filtering by marker. The `unit` marker still works for `pytest -m unit`.
- **Rejected:** Hand-add `@pytest.mark.unit` everywhere (slow, easy to forget). Run everything in CI (needs live Qdrant and Neo4j).

### D-04: Auto-fix lint, relax rules that don't suit scripts
- **Why:** About 600 findings, mostly style. 364 are `print`, which is normal for CLI ingestion scripts, and 46 are magic-number checks. Fixing these by hand adds risk to working code without improving quality. Auto-fix handles about 150, and the config ignores `print` and magic numbers in scripts and tests. Real problems (unused variables, unused imports) are fixed.
- **Rejected:** Remove lint from CI (loses the safety net). Fix all 364 prints (replacing CLI output with logging is a refactor, not a fix).

### D-05: Remove committed `node_modules` and `dist` from git
- **Why:** They are build output and dependencies, around 3000 tracked files. They bloat the repo, slow every CI checkout and cause merge noise. `npm ci` recreates them.
- **Impact:** Only untracks them. Your local copies stay.

### D-06: "Full" means 100 companies — NEEDS YOUR CONFIRMATION
- **Why:** Nothing in the repo defines "full": there are no docs or config with a target number beyond the 10 in `companies.csv`. I picked 100 because it is a meaningful step up from 10 (covering the software, cloud, semiconductor and internet sector you started with), and it is the largest size I expect to fit in free-tier storage (D-10). It also keeps OpenAI graph-extraction cost bounded.
- **Alternatives:** the S&P 500 (about 500 companies, 5× the storage and cost, and won't fit the free tiers), or about 50 (safer, less impressive).
- **Question for you:** Is 100 what you meant, or did you have a different list in mind from the original plan?

### D-07: Wire the real agent into the API; delete the mock
- **Why:** `stream.py` returns fabricated events (a fake MSFT chunk and canned text), which is why the UI "works" but shows nothing real. The real pipeline exists in `agent/runner.py::run_query`. Shipping a fake answer in a public demo would be misleading.
- **Rejected:** Keep the mock as a "demo mode" (confusing, and could be mistaken for real output). If needed later, it must be clearly labelled.

### D-08: POST + fetch streaming instead of EventSource
- **Why:** `EventSource` is GET-only and cannot send custom headers. D-12 needs the OpenAI key in a header. Putting a key in a URL would leak it into logs, history and proxies.
- **Rejected:** Key in query string (insecure). Key in a server-side session (needs storage and cookies, and breaks "never stored").

### D-09: Drop Postgres from compose
- **Why:** It is declared with a `DATABASE_URL`, but I found no code that uses it. Extra service, extra memory, and free hosts have no free Postgres we would need anyway.
- **Rejected:** Keep it "for later". It can be added back when a feature needs it.

### D-10: Fit data into free tiers using quantization and pruning
- **Why:** Qdrant Cloud free is 1 GB and AuraDB Free is 200k nodes and 400k relationships. 100 companies will not fit unmodified. Scalar quantization, on-disk payloads and limiting graph extraction to high-value chunks are standard ways to stay inside the limits without changing the architecture.
- **Gate:** Measure the real size from a 10-company batch before committing. If it still doesn't fit, shrink the public universe and keep the full set for local runs.

### D-11: Hosting stack
- **Choice:** Hugging Face Spaces (Docker) for the API, Cloudflare Pages for the UI, Qdrant Cloud free and Neo4j AuraDB Free for data.
- **Why:** All four are free with no card required. A Space gives about 16 GB RAM, which the API needs for the local embedding and reranker models, and it is much more generous than the 512 MB of most free app hosts. Pages gives a fast global static host with no sleep.
- **Rejected:** Render/Railway/Fly free tiers (small RAM, sleeping, or require a card). Vercel for the API (serverless limits and timeouts for long agent runs, and model files too large). Self-hosted Qdrant/Neo4j on the Space (the disk is ephemeral).
- **Trade-off:** Spaces sleep when idle, so the first request is slow. The UI warns about it.

### D-12: Bring-your-own OpenAI key, sent per request, never stored
- **Why:** You asked that the app ask for a key and run for that person only. Sending the key in a header with each request and building a short-lived OpenAI client means the server never owns or keeps a key, so you pay nothing and users' keys can't leak from a database. The shared corpus is public and read-only, so there is no per-user data to isolate.
- **Key storage in the browser:** `sessionStorage` (gone when the tab closes), not `localStorage`.
- **Consequence:** It needs a code refactor, because the OpenAI key is currently read once from the environment at import time in three modules.
- **Note:** Embeddings and reranking run locally, so only the planner and answer calls are billed to the user.
- **Rejected:** A shared server key with quotas (you pay, and it is abuse-prone). Accounts and a key vault (too heavy for a free demo).

### D-13: Rate limit, strict CORS, read-only DB credentials
- **Why:** A public endpoint can be hammered even when the key is the user's, because compute and database load are yours. CORS is currently `*`; restricting it to the Pages domain stops other sites from using your API. Read-only credentials on Qdrant and Neo4j limit damage if the Space is compromised.

### D-14 (added in Phase 1): Pin-aware lint config and `pythonpath = src`
- **Why:** In a clean environment, CI would fail with `ModuleNotFoundError: founder` because the package is only importable here via the local venv. `pythonpath = src` in `pytest.ini` fixes that. The pinned ruff (0.12) also flagged a deprecated rule (`UP038`) that the newer ruff in the local venv doesn't, so it is ignored.
- **Also:** `ENV PYTHONPATH=/app/src` in the API Dockerfile, for the same import reason.

### D-15 (added in Phase 1): Dropped mypy and the frontend vitest step from CI
- **Why:** The old mypy step was `continue-on-error` (never gated anything) and the codebase has not been type-annotated for it. The frontend has no test runner installed, and the only "test" was a Python file containing `assert True`. CI instead runs `tsc --noEmit` plus the production build for the frontend. Real tests can be added in Phase 2 together with the UI changes.
