# FounderOS: Fix, Scale, Deploy Plan

Every choice made here is logged in [decision.md](decision.md) as D-xx. Read that file to see why.

## 0. What I found (root causes)

### A. Why GitHub Actions fails everywhere
The git root is `FounderOS/`, but the Python project lives in `founder/` and the UI in `frontend/`.

| # | Finding | Effect |
|---|---|---|
| A1 | `test.yml` runs `pip install -r requirements.txt` and `ruff check src/ tests/` from the repo root. Those files are in `founder/`. | Every Python job fails immediately: "requirements.txt not found". |
| A2 | `requirements.txt` lacks `fastapi`, `uvicorn`, `pydantic-settings`, `pytest`, `httpx` and `langfuse`. A local run fails with `ModuleNotFoundError: pydantic_settings`. | Tests fail to collect. The API Docker image would also crash on start. |
| A3 | Workflow runs `pytest -m unit`, but almost no test carries a `unit` marker. Only 2 tests are marked, both `integration`. | pytest selects 0 tests and exits with code 5, which fails the job. |
| A4 | `pytest.ini` has `--strict-markers`, and `pyproject.toml` adds `--cov` options. | Config conflicts and strict-marker errors. |
| A5 | `ruff check` reports about 600 issues (364 `print`, 65 import order, 46 magic values, and others). | The lint step fails. |
| A6 | The matrix includes Python 3.10 and 3.11, but the project was built on 3.13, and Kedro 1.6 and scikit-learn 1.8 are pinned. | Likely resolver failures on 3.10. |
| A7 | `build.yml` uses `upload-artifact@v3` (retired, so it errors), and `workflow_run` chaining runs duplicates. | The build job fails. |
| A8 | `frontend/node_modules/` and `frontend/dist/` are committed (about 3070 tracked files). `package.json` has a `lint` script but no eslint, `tsc` runs in the build, and Node 18 is end-of-life. | Noise and slow checkouts; a possible type error in the build. |
| A9 | The Docker build runs `COPY src/` and `COPY conf/`, but the broken requirements mean the image cannot run. | The Docker build step fails or the container crashes. |

### B. Why `npm run dev` opens a page where "nothing works"
1. **The backend query endpoint is a stub.** `founder/src/founder/api/routes/stream.py` returns hard-coded fake events: a fake MSFT chunk, then the text "Based on the financial documents analyzed…". It never calls the real agent in `agent/runner.py::run_query`. The real pipeline (LangGraph agent, Qdrant, Neo4j, XBRL) exists but has no API route.
2. The UI does nothing useful unless the API (port 8000), Qdrant and Neo4j are all running. Nothing tells the user which one is missing.
3. `api.ts` has a hard-coded `http://localhost:8000` for health checks, a relative `/api` for streaming, and no configurable base URL. This breaks once deployed.
4. The streaming endpoint is GET-only via `EventSource`, which cannot send an API-key header.

### C. What "frontend and Docker" are for
- **Frontend (React/Vite console):** the user-facing product. A person types a question and sees the answer, citations, evidence cards, contradictions and a timeline. Without it, the project is only CLI scripts.
- **Docker / compose:** one command (`docker compose up`) starts Qdrant, Neo4j, Postgres, the API and the UI together. It is also the unit that every free host deploys. Today it is dev-only, and Postgres is declared but unused.

### D. "Ten companies" is a data limit, not a code limit
`founder/data/companies.csv` has 10 tickers (MSFT, CRM, NOW, ADBE, AMZN, DDOG, NVDA, PLTR, SHOP, SNOW). All ingestion reads that CSV (`ingestion/sec.py`), so scaling is mostly a change to that CSV. It is limited by downloads, OpenAI cost, vector storage and free-tier limits. Current corpus: 2.1 GB raw (1.8 GB of it earnings transcripts), 128 MB of chunks. All of it is git-ignored, so CI and hosts have no data.

The repo does not define a number for "full". The plan assumes 100 companies (D-06). Correct me if you meant something else.

---

## Phase 1: Make CI green: DONE (see "Phase 1 result" at the end)

1. **Restructure workflows** (D-01). Set `defaults.run.working-directory: founder`, run on a single Python 3.12 job, and fix the `cache-dependency-path`.
2. **Split requirements** (D-02). Create `requirements.txt` for runtime only (add fastapi, uvicorn, pydantic-settings, langfuse, httpx) and `requirements-dev.txt` with pytest, pytest-cov, ruff and httpx. Move Jupyter, Kedro-Viz and notebook out of the runtime image.
3. **Fix test selection** (D-03). Auto-mark tests with `conftest.py` (marking tests that touch Qdrant, Neo4j or network as `integration`, and the rest as `unit`). CI runs `pytest -m "not integration"`. Remove the duplicate `--cov` options so there is a single source.
4. **Lint** (D-04). Run `ruff --fix` for the auto-fixable issues (about 150). Change the ruff config to ignore `T201` and `PLR2004` for scripts and tests. Fix the remaining real issues (unused variables, unused imports). CI fails only on real errors.
5. **Build workflow:** upgrade to `upload-artifact@v4`, drop `workflow_run`, and build the Docker images with `docker/build-push-action@v6`. Test job and build job are separate jobs in one workflow.
6. **Frontend job:** Node 20, `npm ci`, `tsc --noEmit`, `npm run build`, plus vitest for a minimal test. Add eslint to match the `lint` script, or remove the script.
7. **Repo hygiene:** `git rm -r --cached frontend/node_modules frontend/dist`, add a root `.gitignore` (node_modules, dist, venv, `.env`, `*.log`, `info.log`) and confirm `founder/.env` and `conf/local/.env` were never committed (history check; rotate the key if they were).
8. **Delete the placeholder test** `frontend/tests/test_frontend.py` or replace it with real vitest tests.

**Done when:** a push to `main` shows all-green Tests and Build workflows, and a PR shows the same.

## Phase 2: Make the app actually work (about 2 days)

1. **Replace the mock stream** (D-07). `stream.py` calls the real `run_query`/LangGraph app, and emits real status events from graph nodes (planner, retrieval, sufficiency, synthesis) over SSE. Keep the existing event schemas so the UI keeps working.
2. **Switch to POST streaming** (D-08). The frontend uses `fetch` with a readable stream so it can send headers (the OpenAI key) in a header, never the URL.
3. **Config:** `VITE_API_BASE_URL` for the frontend; remove the hard-coded localhost.
4. **Health that means something:** `/health` returns the status of Qdrant, Neo4j and whether the corpus is loaded; the UI shows a clear banner such as "Neo4j is down" or "No data loaded".
5. **Make the UI usable:** an example-questions row (the five demo scenarios from the README), an empty state, error display and a loading state. Add the company filter and timeline views to the page if not wired.
6. **Dockerfiles:**
   - API: multi-stage build, non-root user, runtime requirements only, healthcheck with `curl`/`urllib`.
   - Frontend: build with Node 20, serve with nginx, and proxy `/api` to the API.
   - Compose: remove the `./src` and `./conf` bind mounts from the production file (keep them in `docker-compose.dev.yml`), pin image versions, remove the unused Postgres service (D-09).
7. **Local acceptance test:** `docker compose up`, then ask the five README questions in the browser and get real, cited answers.

**Done when:** the UI shows a real answer with citations from the 10-company data, and the e2e smoke test passes in CI against mocked retrievers.

## Phase 3: Scale to the full company set (about 1 week, mostly waiting on downloads)

1. **Define the universe** (D-06): `data/universe/companies.csv`, 100 tickers (the current 10 plus about 90 software, cloud, semiconductor and internet names), with sector and CIK. The 10-company set stays as a small `--profile demo` fixture for tests.
2. **Parametrize ingestion:** every stage takes `--universe` and `--tickers`, and skips completed work (idempotent, resumable). The state is stored in a manifest file.
3. **Run in batches of 10 companies,** in this order:
   1. SEC submissions, filings, XBRL facts (free, rate-limited to 10 requests/sec by SEC; the project already sends a User-Agent).
   2. Earnings transcripts (check the source's terms and rate limit; see Risks).
   3. News (check the API quota).
   4. Chunking and validation (`validate_chunks.py` gates every batch).
   5. Embeddings are local (fastembed), so no OpenAI cost.
   6. Graph extraction, the only expensive OpenAI step. Measure the cost per company on the first batch, then extrapolate. Use `gpt-4o-mini`.
4. **Storage budget** (D-10): set Qdrant payload to on-disk, use scalar quantization, and drop the full text from the payload where a fetch by ID is cheaper. Compute the chunk count and vector size before uploading.
5. **Neo4j budget:** the AuraDB Free limit is 200k nodes / 400k relationships. Prune low-value entity types or restrict extraction to the highest-signal chunk types, if the estimate is above the limit.
6. **Evaluation:** grow `data/05_evaluation` to the 100-question target from `FOUNDEROS_REMAINING_PLAN.md`, then run `run_release_baseline` before and after scaling, so quality regression is visible.

**Done when:** all 100 companies are indexed, `validate_chunks` passes, and the baseline metrics are published in `docs/evaluation/BASELINE.md`.

## Phase 4: Free public deployment, bring-your-own OpenAI key (about 2 days)

### Architecture (D-11)
```
Browser (user enters OpenAI key, kept in sessionStorage only)
   │  HTTPS, key sent per request in header X-OpenAI-Key
   ▼
Cloudflare Pages ──(static React build)
   │
   ▼
Hugging Face Space (Docker, free CPU, 16 GB RAM): FastAPI + local embeddings + reranker
   ├─► Qdrant Cloud free cluster (1 GB)    [read-only shared public-filing corpus]
   └─► Neo4j AuraDB Free                    [read-only shared graph]
```

### How "runs for that person only" works (D-12)
- The corpus is public SEC and earnings data, so it is shared and read-only. Nothing about a visitor is stored.
- The visitor's key is sent with each request, used to construct a request-scoped OpenAI client, and discarded. It is never written to logs, to Langfuse or to disk, and it is masked in error messages.
- This requires refactoring the module-level `OPENAI_API_KEY` constants in `agent/config.py`, `graph/config.py` and `generation/answer.py` to a request-scoped client (ContextVar), plus a redaction filter on logging.
- No key means a clear 401 response ("Add your OpenAI key"). The server has no OpenAI key of its own, so the maintainer pays nothing.
- Only the LLM calls (planning and synthesis) use the visitor's key. Embeddings and reranking run locally, which makes the per-query cost a few cents.

### Abuse and safety (D-13)
- Per-IP rate limit (for example 20 requests/minute) and a request timeout.
- Strict CORS: only the Pages domain (remove `allow_origins=["*"]`).
- Max query length, `top_k` cap, and the read-only database credentials for Qdrant and Neo4j.
- A cold-start note in the UI (free Spaces sleep after inactivity).

### Steps
1. Create the Qdrant Cloud and AuraDB Free instances, and load the data with a one-off `scripts/load_to_cloud.py` (resumable).
2. Add a `Dockerfile.hf` for the Space (port 7860), set the secrets for Qdrant and Neo4j in Space settings.
3. Add the "Enter your OpenAI key" screen with a short privacy note. Validate the key with a cheap call before use.
4. Deploy the frontend to Cloudflare Pages with `VITE_API_BASE_URL` set to the Space URL.
5. Add the `deploy.yml` workflow: on `main`, after tests pass, push to the HF Space (git push with a token secret) and Cloudflare Pages deploys from the repo.
6. Post-deploy smoke test: `/health`, then one canned query using a test key kept in GitHub secrets.
7. README: live URL, an architecture diagram, a 60-second demo GIF, and the evaluation badges.

**Done when:** a stranger can open the URL, paste a key, and get a cited answer, with no cost to you.

---

## Risks and open questions

| Risk | Mitigation |
|---|---|
| "Full" scope is undefined. | Assumed 100 companies (D-06). Confirm. |
| Qdrant 1 GB or AuraDB 200k-node limits are exceeded by 100 companies. | Measure first (Phase 3.4 and 3.5), then use quantization and pruning. Fallback: shrink the public universe and keep the full set for local use. |
| Earnings transcript and news sources may have licensing or rate limits (the 1.8 GB transcript dataset is large). | Check the terms before redistributing in a public demo. Redistributing may need excerpts only. |
| Free Spaces sleep and are slow on a cold start. | UI warning and a keep-alive ping on the `/health` endpoint. |
| A user-supplied key can be leaked through logs. | Redaction filter, tests that assert the key never appears in logs or traces. |
| `founder/.env` may hold a real key. | Verify it is not in git history, and rotate it if it is. |

## Suggested order of work
Phase 1 (CI green) → Phase 2 (working app locally) → Phase 4 steps 2–4 with the 10-company data (a live, working demo early) → Phase 3 (scale) → reload the cloud data.
This gets a public demo online before the slowest step, the scale-up.

---

## Phase 1 result
Verified in a clean virtualenv built only from `requirements-dev.txt`: ruff passes and 114 tests pass (1 skipped on purpose). A runtime-only venv imports the API and agent. Not verified here: the GitHub Actions run itself (needs a push) and the Docker image builds (Docker Desktop was not running).

Changes: one `ci.yml` replacing `test.yml` and `build.yml`; requirements split into 4 files; auto-marking in `conftest.py`; `pythonpath = src`; ruff config plus about 150 auto-fixes; `node_modules` and `dist` untracked; root `.gitignore`; `.dockerignore` files that keep the 2.4 GB `data/` and `conf/local/.env` out of the image; Node 20; `tsc --noEmit` in the frontend build.
