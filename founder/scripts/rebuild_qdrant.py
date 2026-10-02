"""Rebuild Qdrant vector indexes from chunks."""

from pathlib import Path


def rebuild_qdrant():
    """Index chunks into Qdrant."""

    chunks_path = Path("data/04_chunks/chunks.jsonl")

    if not chunks_path.exists():

        print(f"[ERROR] {chunks_path} not found. Run rebuild_dataset.py first.")

        return

    print("Rebuilding Qdrant indexes...")

    print("Would connect to Qdrant at http://localhost:6333")

    print("Would create collections: documents, earnings, news, facts")

    print("Would index chunks with dense + sparse embeddings")

    # Count chunks
    with open(chunks_path) as f:

        count = sum(1 for _ in f)

    print(f"[OK] Would index {count} chunks to Qdrant")


if __name__ == "__main__":
    rebuild_qdrant()
