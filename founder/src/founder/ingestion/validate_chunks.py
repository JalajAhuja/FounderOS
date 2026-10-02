import json
from pathlib import Path
from collections import Counter


CHUNKS_FILE = Path(
    "data/04_chunks/chunks.jsonl"
)


def main():

    print("\n" + "=" * 70)
    print("FounderOS - Chunk Validation")
    print("=" * 70)

    if not CHUNKS_FILE.exists():
        print(
            f"ERROR: {CHUNKS_FILE} does not exist."
        )
        return

    chunks = []

    with open(
        CHUNKS_FILE,
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
                chunks.append(
                    json.loads(line)
                )

            except json.JSONDecodeError as e:
                print(
                    f"Invalid JSON at line "
                    f"{line_number}: {e}"
                )

    print(
        f"\nTotal chunks: {len(chunks):,}"
    )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "chunk_id",
        "document_id",
        "text",
        "source",
        "ticker",
        "document_type",
        "section",
        "chunk_index",
        "token_count",
    ]

    print("\nChecking required fields...")

    field_errors = 0

    for index, chunk in enumerate(chunks):

        for field in required_fields:

            if field not in chunk:

                print(
                    f"Missing '{field}' "
                    f"at chunk {index}"
                )

                field_errors += 1

                if field_errors >= 20:
                    break

        if field_errors >= 20:
            break

    if field_errors == 0:
        print("OK - required fields present.")

    else:
        print(
            f"ERRORS: {field_errors}"
        )

    # --------------------------------------------------------
    # Duplicate IDs
    # --------------------------------------------------------

    print("\nChecking duplicate chunk IDs...")

    ids = [
        chunk.get("chunk_id")
        for chunk in chunks
    ]

    counts = Counter(ids)

    duplicates = [
        chunk_id
        for chunk_id, count in counts.items()
        if count > 1
    ]

    if duplicates:

        print(
            f"ERROR - duplicate IDs: "
            f"{len(duplicates)}"
        )

        for chunk_id in duplicates[:10]:
            print(
                f"  {chunk_id}"
            )

    else:
        print(
            "OK - no duplicate chunk IDs."
        )

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    print("\nChunk distribution by source:")

    source_counts = Counter(
        chunk.get("source")
        for chunk in chunks
    )

    for source, count in sorted(
        source_counts.items()
    ):

        print(
            f"  {source}: {count:,}"
        )

    # --------------------------------------------------------
    # Tickers
    # --------------------------------------------------------

    print("\nChunk distribution by ticker:")

    ticker_counts = Counter(
        chunk.get("ticker")
        for chunk in chunks
    )

    for ticker, count in sorted(
        ticker_counts.items()
    ):

        print(
            f"  {ticker}: {count:,}"
        )

    # --------------------------------------------------------
    # Token statistics
    # --------------------------------------------------------

    token_counts = [
        chunk.get(
            "token_count",
            0
        )
        for chunk in chunks
    ]

    if token_counts:

        print("\nToken statistics:")

        print(
            f"  Minimum: {min(token_counts)}"
        )

        print(
            f"  Maximum: {max(token_counts)}"
        )

        print(
            f"  Average: "
            f"{sum(token_counts) / len(token_counts):.1f}"
        )

    # --------------------------------------------------------
    # Empty chunks
    # --------------------------------------------------------

    empty_chunks = [
        chunk
        for chunk in chunks
        if not chunk.get("text", "").strip()
    ]

    print("\nEmpty chunks:")

    if empty_chunks:
        print(
            f"ERROR - {len(empty_chunks)} empty chunks"
        )
    else:
        print("OK - no empty chunks.")

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    if (
        field_errors == 0
        and not duplicates
        and not empty_chunks
    ):

        print(
            "VALIDATION PASSED"
        )

    else:

        print(
            "VALIDATION FAILED"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()