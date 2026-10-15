import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# PATHS
# ============================================================

CHUNKS_FILE = Path(
    "data/04_chunks/chunks.jsonl"
)

EXTRACTIONS_FILE = Path(
    "data/04_chunks/graph_extractions.jsonl"
)


# ============================================================
# NEO4J
# ============================================================

NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://localhost:7687",
)

NEO4J_USERNAME = os.getenv(
    "NEO4J_USERNAME",
    "neo4j",
)

NEO4J_PASSWORD = os.getenv(
    "NEO4J_PASSWORD",
    "founderos_password",
)

NEO4J_DATABASE = os.getenv(
    "NEO4J_DATABASE",
    "neo4j",
)


# ============================================================
# OPENAI
# ============================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

OPENAI_MODEL = os.getenv(
    "OPENAI_GRAPH_MODEL",
    "gpt-5.6-luna",
)


# ============================================================
# EXTRACTION
# ============================================================

# Start small while testing.
# Set to None to process everything.
MAX_CHUNKS = None

BATCH_SIZE = 5
