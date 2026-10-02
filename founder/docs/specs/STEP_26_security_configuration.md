# Step 26 — Security + Configuration Hardening

## Goal

Make FounderOS safe to deploy to production and push to public GitHub.

## Non-goals

- OAuth/SAML authentication (that's Step 27+)
- Rate limiting (that's Step 27+)
- API key rotation (manual for now)

## Inputs

- Existing codebase with hardcoded config references
- Environment variables scattered across modules

## Outputs

```text
src/founder/config/
├── __init__.py
├── settings.py
└── validation.py

.env.example
.env (ignored by git)
.gitignore (updated)
tests/test_config.py
```

## Architecture

Centralized settings:

```python
class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"
    
    # Qdrant
    qdrant_url: str
    qdrant_api_key: str | None = None
    
    # Neo4j
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    # Database
    database_url: str
    
    # Langfuse
    langfuse_enabled: bool = False
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Reranker
    reranker_enabled: bool = True
    reranker_model: str = "Xenova/ms-marco-MiniLM-L-6-v2"
    
    # App
    app_env: str = "development"  # development | production
    log_level: str = "INFO"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

## Files to create

```text
src/founder/config/__init__.py
src/founder/config/settings.py
src/founder/config/validation.py

.env.example
tests/config/test_settings.py
```

## Files to modify

```text
.gitignore  (add .env)
src/founder/settings.py  (consolidate with new config)
src/founder/__main__.py  (call validate_settings on startup)
```

## Data contracts

None (settings are internal).

## Validation rules

Required (must fail fast):

```python
OPENAI_API_KEY
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
QDRANT_URL
```

Optional but configured:

```python
LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY
DATABASE_URL
```

Defaults:

```python
RERANKER_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"
LOG_LEVEL = "INFO"
APP_ENV = "development"
```

## .env.example

```text
# Required
OPENAI_API_KEY=sk-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
QDRANT_URL=http://localhost:6333

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/founder

# Optional: Langfuse
LANGFUSE_ENABLED=false
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

# Reranker
RERANKER_ENABLED=true
RERANKER_MODEL=Xenova/ms-marco-MiniLM-L-6-v2

# Application
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=false
```

## Error handling

- Missing required setting: exit with clear error message
- Invalid URL format: raise ValueError
- Invalid log level: default to INFO and warn
- Connection test on startup (optional)

## Observability

- Log which settings are loaded
- Warn if APP_ENV=production with DEBUG=true
- Log secrets as ****
- Record config validation result

## Tests

- Test required settings validation
- Test optional settings with defaults
- Test invalid values (bad URLs, etc.)
- Test case-insensitivity
- Test environment variable override

## Acceptance criteria

- `pytest -q tests/config/` passes
- `python -m founder.__main__` fails with clear error if settings missing
- Secrets never logged
- .env file not in git
- .env.example is in git

## Startup sequence

1. Load .env file
2. Load environment variables
3. Create Settings object
4. Validate required settings
5. Test database connection (optional)
6. Log loaded config (secrets redacted)
7. Start application

## Rollback / recovery

If settings invalid, application refuses to start (fail-fast).

## Known limitations

- No automatic rotation of secrets
- No vault integration (use external secret manager)
- No per-environment config files (use env vars only)
