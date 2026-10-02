"""Application settings and configuration."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central application settings from environment variables."""

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"

    # Qdrant
    qdrant_url: str
    qdrant_api_key: Optional[str] = None

    # Neo4j
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str

    # Database
    database_url: Optional[str] = None

    # Langfuse
    langfuse_enabled: bool = False
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"

    # Reranker
    reranker_enabled: bool = True
    reranker_model: str = "Xenova/ms-marco-MiniLM-L-6-v2"

    # Application
    app_env: str = "development"  # development | production | test
    log_level: str = "INFO"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global Settings instance."""

    global _settings

    if _settings is None:
        _settings = Settings()

    return _settings


def validate_settings() -> None:
    """Validate all required settings on startup."""

    settings = get_settings()

    required_fields = [
        "openai_api_key",
        "qdrant_url",
        "neo4j_uri",
        "neo4j_username",
        "neo4j_password",
    ]

    missing = []

    for field in required_fields:

        value = getattr(settings, field, None)

        if not value:
            missing.append(field)

    if missing:

        raise ValueError(
            f"Missing required settings: {', '.join(missing)}\n"
            f"Please check your .env file or environment variables."
        )

    if settings.app_env == "production" and settings.debug:

        import warnings

        warnings.warn(
            "DEBUG=true in production mode is insecure. "
            "Set DEBUG=false.",
            RuntimeWarning,
        )
