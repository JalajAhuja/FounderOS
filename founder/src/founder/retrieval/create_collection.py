from qdrant_client import QdrantClient, models

from founder.retrieval.config import (
    COLLECTION_NAME,
    DENSE_VECTOR_NAME,
    QDRANT_URL,
    SPARSE_VECTOR_NAME,
)

DENSE_VECTOR_SIZE = 768


def main():

    print("\n" + "=" * 70)
    print("FounderOS - Create Qdrant Collection")
    print("=" * 70)

    client = QdrantClient(
        url=QDRANT_URL
    )

    print(
        f"\nQdrant: {QDRANT_URL}"
    )

    # --------------------------------------------------------
    # Remove old collection if it exists
    # --------------------------------------------------------

    if client.collection_exists(
        COLLECTION_NAME
    ):

        print(
            f"Collection already exists: "
            f"{COLLECTION_NAME}"
        )

        answer = input(
            "Delete and recreate it? [y/N]: "
        ).strip().lower()

        if answer == "y":

            client.delete_collection(
                COLLECTION_NAME
            )

            print(
                "Existing collection deleted."
            )

        else:

            print(
                "Keeping existing collection."
            )

            return

    # --------------------------------------------------------
    # Create collection
    # --------------------------------------------------------

    client.create_collection(

        collection_name=COLLECTION_NAME,

        vectors_config={
            DENSE_VECTOR_NAME:
                models.VectorParams(
                    size=DENSE_VECTOR_SIZE,
                    distance=models.Distance.COSINE,
                )
        },

        sparse_vectors_config={
            SPARSE_VECTOR_NAME:
                models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                )
        },
    )

    # --------------------------------------------------------
    # Payload indexes
    # --------------------------------------------------------

    payload_fields = {
        "ticker": models.PayloadSchemaType.KEYWORD,
        "source": models.PayloadSchemaType.KEYWORD,
        "document_type": models.PayloadSchemaType.KEYWORD,
        "section": models.PayloadSchemaType.KEYWORD,
        "year": models.PayloadSchemaType.INTEGER,
        "quarter": models.PayloadSchemaType.INTEGER,
    }

    for field_name, field_type in (
        payload_fields.items()
    ):

        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field_name,
            field_schema=field_type,
        )

    # --------------------------------------------------------
    # Verify
    # --------------------------------------------------------

    info = client.get_collection(
        COLLECTION_NAME
    )

    print("\nCollection created successfully.")

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print(
        f"Points: {info.points_count}"
    )

    print(
        "\nVectors:"
    )

    print(
        f"  Dense:  {DENSE_VECTOR_NAME}"
    )

    print(
        f"  Sparse: {SPARSE_VECTOR_NAME}"
    )

    print(
        "\n" + "=" * 70
    )


if __name__ == "__main__":
    main()
