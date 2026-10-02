"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_query() -> str:
    """Sample query for testing."""
    return "What did Microsoft say about AI monetization?"


@pytest.fixture
def sample_evidence() -> dict:
    """Sample evidence object."""
    return {
        "evidence_id": "test-chunk-1",
        "source": "SEC",
        "text": "Microsoft discussed AI monetization in earnings call.",
        "score": 0.95,
        "ticker": "MSFT",
        "published_at": "2025-06-01",
    }


@pytest.fixture
def sample_answer() -> dict:
    """Sample answer object."""
    return {
        "text": "Microsoft's AI monetization strategy focuses on cloud services.",
        "claims": [
            {
                "text": "Microsoft emphasizes cloud AI services.",
                "evidence_ids": ["test-chunk-1"],
                "claim_type": "source_claim",
                "confidence": 0.92,
            }
        ],
        "citations": [
            {
                "citation_id": 1,
                "evidence_id": "test-chunk-1",
                "source": "SEC",
                "date": "2025-06-01",
            }
        ],
        "limitations": ["Limited to publicly available information."],
    }


@pytest.fixture
def sample_settings() -> dict:
    """Sample settings for testing."""
    return {
        "OPENAI_API_KEY": "sk-test-key",
        "QDRANT_URL": "http://localhost:6333",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "test-password",
    }
