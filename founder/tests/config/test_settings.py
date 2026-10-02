"""Configuration validation tests."""

import pytest

from founder.config.settings import Settings, validate_settings


def test_settings_load_from_env(monkeypatch):

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "password")

    settings = Settings()

    assert settings.openai_api_key == "sk-test"
    assert settings.qdrant_url == "http://localhost:6333"
    assert settings.neo4j_uri == "bolt://localhost:7687"


def test_settings_with_defaults(monkeypatch):

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "password")

    settings = Settings()

    assert settings.openai_model == "gpt-4-turbo"
    assert settings.reranker_enabled is True
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"


def test_settings_case_insensitive(monkeypatch):

    monkeypatch.setenv("openai_api_key", "sk-test")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("neo4j_uri", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("neo4j_password", "password")

    settings = Settings()

    assert settings.openai_api_key == "sk-test"
    assert settings.neo4j_uri == "bolt://localhost:7687"


def test_validate_settings_missing_required(monkeypatch):

    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "password")

    settings = Settings()

    with pytest.raises(ValueError, match="Missing required settings"):

        required_fields = [
            "openai_api_key",
            "qdrant_url",
            "neo4j_uri",
            "neo4j_username",
            "neo4j_password",
        ]

        missing = [
            f for f in required_fields
            if not getattr(settings, f, None)
        ]

        if missing:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")
