# Step 28 — Dockerize the Application

## Goal

Create reproducible local and production-like environments with all services
(Qdrant, Neo4j, PostgreSQL, API, Frontend) in a single compose stack.

## Non-goals

- Kubernetes deployment (that's Step 32+)
- Multi-environment templates (use .env overrides)

## Inputs

- Existing Dockerfile patterns (if any)
- docker-compose.yml template

## Outputs

```text
docker-compose.yml (updated)
Dockerfile (backend)
frontend/Dockerfile
.dockerignore
```

## Services

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports: 6333:6333
    volumes: qdrant_data:/qdrant/storage
    healthcheck: GET http://localhost:6333/health

  neo4j:
    image: neo4j:latest
    ports: 7687:7687, 7474:7474
    volumes: neo4j_data:/data
    environment: NEO4J_AUTH=neo4j/founderos_password
    healthcheck: neo4j status

  postgres:
    image: postgres:15-alpine
    ports: 5432:5432
    volumes: postgres_data:/var/lib/postgresql/data
    environment: POSTGRES_PASSWORD=postgres
    healthcheck: pg_isready

  api:
    build: .
    ports: 8000:8000
    depends_on:
      - qdrant
      - neo4j
      - postgres
    environment: (from .env)
    command: uvicorn founder.api.main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports: 3000:3000
    depends_on:
      - api
```

## Files to create

```text
Dockerfile (backend)
frontend/Dockerfile
.dockerignore
docker-compose.yml (updated)
```

## Requirements

- No hardcoded secrets in compose
- All configuration from .env
- Health checks for all services
- Named volumes for data persistence
- Restart policies (restart: unless-stopped)
- Service dependency ordering

## Acceptance criteria

- `docker compose up -d --build` succeeds
- `docker compose ps` shows all services running
- `curl http://localhost:8000/health` returns 200
- Frontend accessible at http://localhost:3000

## Developer verification

```powershell
docker compose down
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
```

## Known limitations

- No load balancer (single-machine deployment)
- No log aggregation
- Workers not included yet (Step 32+)
