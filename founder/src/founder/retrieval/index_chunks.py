import json
import uuid
from pathlib import Path

from fastembed import (
    SparseTextEmbedding,
    TextEmbedding,
)

from qdrant_client import (
    QdrantClient,
    models,
)

from founder.retrieval.config import (
    CHUNKS_FILE,
    QDRANT_URL,
    COLLECTION_NAME,
    DENSE_MODEL_NAME,
    SPARSE_MODEL_NAME,
    DENSE_VECTOR_NAME,
    SPARSE_VECTOR_NAME,
    BATCH_SIZE,
)


# ============================================================
# HELPERS
# ============================================================

def read_jsonl_batches(
    path: Path,
    batch_size: int,
):

    batch = []

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        for line_number, line in enumerate(
            f,
            start=1,
        ):

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(
                    line
                )

            except json.JSONDecodeError as e:

                print(
                    f"WARNING: invalid JSON "
                    f"at line {line_number}: "
                    f"{e}"
                )

                continue

            batch.append(record)

            if len(batch) >= batch_size:

                yield batch

                batch = []

    if batch:
        yield batch


def make_point_id(chunk_id: str):

    """
    Qdrant point IDs must be integers or UUIDs.

    We deterministically convert our chunk_id
    into UUID5 so the same chunk always receives
    the same point ID.
    """

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"founderos:{chunk_id}",
        )
    )


def build_payload(chunk):

    return {
        "chunk_id": chunk.get(
            "chunk_id"
        ),

        "document_id": chunk.get(
            "document_id"
        ),

        "text": chunk.get(
            "text",
            "",
        ),

        "source": chunk.get(
            "source"
        ),

        "ticker": chunk.get(
            "ticker"
        ),

        "document_type": chunk.get(
            "document_type"
        ),

        "section": chunk.get(
            "section"
        ),

        "speaker": chunk.get(
            "speaker"
        ),

        "year": chunk.get(
            "year"
        ),

        "quarter": chunk.get(
            "quarter"
        ),

        "published_at": chunk.get(
            "published_at"
        ),

        "chunk_index": chunk.get(
            "chunk_index"
        ),

        "token_count": chunk.get(
            "token_count"
        ),

        "metadata": chunk.get(
            "metadata",
            {},
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("FounderOS - Chunk Embedding + Qdrant Indexing")
    print("=" * 70)

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not CHUNKS_FILE.exists():

        raise FileNotFoundError(
            f"Chunks file not found: "
            f"{CHUNKS_FILE}"
        )

    # --------------------------------------------------------
    # Qdrant
    # --------------------------------------------------------

    print(
        f"\nConnecting to Qdrant: "
        f"{QDRANT_URL}"
    )

    client = QdrantClient(
        url=QDRANT_URL
    )

    if not client.collection_exists(
        COLLECTION_NAME
    ):

        raise RuntimeError(
            f"Collection '{COLLECTION_NAME}' "
            f"does not exist.\n"
            f"Run create_collection.py first."
        )

    # --------------------------------------------------------
    # Load embedding models
    # --------------------------------------------------------

    print(
        "\nLoading dense model:"
    )

    print(
        f"  {DENSE_MODEL_NAME}"
    )

    dense_model = TextEmbedding(
        model_name=DENSE_MODEL_NAME
    )

    print(
        "\nLoading sparse model:"
    )

    print(
        f"  {SPARSE_MODEL_NAME}"
    )

    sparse_model = SparseTextEmbedding(
        model_name=SPARSE_MODEL_NAME
    )

    print(
        "\nModels loaded."
    )

    # --------------------------------------------------------
    # Index batches
    # --------------------------------------------------------

    total = 0

    for batch_number, batch in enumerate(
        read_jsonl_batches(
            CHUNKS_FILE,
            BATCH_SIZE,
        ),
        start=1,
    ):

        texts = []

        valid_chunks = []

        for chunk in batch:

            text = str(
                chunk.get(
                    "text",
                    ""
                )
            ).strip()

            chunk_id = chunk.get(
                "chunk_id"
            )

            if not text:
                continue

            if not chunk_id:
                continue

            valid_chunks.append(
                chunk
            )

            # Passage embedding.
            texts.append(
                text
            )

        if not valid_chunks:
            continue

        # ----------------------------------------------------
        # Dense embeddings
        # ----------------------------------------------------

        dense_embeddings = list(
            dense_model.passage_embed(
                texts
            )
        )

        # ----------------------------------------------------
        # Sparse embeddings
        # ----------------------------------------------------

        sparse_embeddings = list(
            sparse_model.passage_embed(
                texts
            )
        )

        # ----------------------------------------------------
        # Build Qdrant points
        # ----------------------------------------------------

        points = []

        for (
            chunk,
            dense_vector,
            sparse_vector,
        ) in zip(
            valid_chunks,
            dense_embeddings,
            sparse_embeddings,
        ):

            point_id = make_point_id(
                chunk["chunk_id"]
            )

            point = models.PointStruct(

                id=point_id,

                vector={

                    DENSE_VECTOR_NAME:
                        dense_vector.tolist(),

                    SPARSE_VECTOR_NAME:
                        models.SparseVector(
                            indices=(
                                sparse_vector
                                .indices
                                .tolist()
                            ),
                            values=(
                                sparse_vector
                                .values
                                .tolist()
                            ),
                        ),
                },

                payload=build_payload(
                    chunk
                ),
            )

            points.append(point)

        # ----------------------------------------------------
        # Upsert
        # ----------------------------------------------------

        client.upsert(

            collection_name=COLLECTION_NAME,

            points=points,

            wait=True,
        )

        total += len(points)

        print(
            f"Batch {batch_number:04d} | "
            f"indexed {len(points):03d} | "
            f"total {total:,}"
        )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    info = client.get_collection(
        COLLECTION_NAME
    )

    print("\n" + "=" * 70)
    print("INDEXING COMPLETE")
    print("=" * 70)

    print(
        f"Indexed chunks: {total:,}"
    )

    print(
        f"Qdrant points:  {info.points_count:,}"
    )

    print(
        f"Collection:     {COLLECTION_NAME}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()