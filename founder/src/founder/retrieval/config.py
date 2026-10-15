from pathlib import Path

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(".")

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "04_chunks"
    / "chunks.jsonl"
)


# ============================================================
# QDRANT
# ============================================================

QDRANT_URL = "http://localhost:6333"

COLLECTION_NAME = "founderos_chunks"


# ============================================================
# EMBEDDING MODELS
# ============================================================

DENSE_MODEL_NAME = (
    "jinaai/jina-embeddings-v2-base-en"
)

SPARSE_MODEL_NAME = (
    "Qdrant/bm25"
)


# ============================================================
# VECTOR NAMES
# ============================================================

DENSE_VECTOR_NAME = "dense"

SPARSE_VECTOR_NAME = "sparse"


# ============================================================
# INDEXING
# ============================================================

BATCH_SIZE = 32


# Number of candidates retrieved independently
# by dense and sparse search before RRF.
PREFETCH_LIMIT = 30


# Final number of results returned to the application.
DEFAULT_TOP_K = 8
