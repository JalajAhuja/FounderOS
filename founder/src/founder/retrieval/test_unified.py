from founder.retrieval.unified_retriever import (
    UnifiedRetriever,
)


def main():

    retriever = UnifiedRetriever()

    print(
        "\n" + "=" * 70
    )

    print(
        "FounderOS Unified Retrieval"
    )

    print(
        "=" * 70
    )

    try:

        while True:

            query = input(
                "\nFounderOS> "
            ).strip()

            if query.lower() in {
                "exit",
                "quit",
                "q",
            }:
                break

            if not query:
                continue

            result = retriever.search(
                query
            )

            print(
                "\n" + "-" * 70
            )

            print(
                f"Evidence returned: "
                f"{len(result['evidence'])}"
            )

            print(
                "-" * 70
            )

            for index, item in enumerate(
                result["evidence"],
                start=1,
            ):

                print(
                    f"\n[{index}] "
                    f"{item.source}"
                )

                print(
                    f"Score: "
                    f"{item.score:.4f}"
                )

                print(
                    f"Ticker: "
                    f"{item.ticker}"
                )

                print(
                    f"Document: "
                    f"{item.document_type}"
                )

                print(
                    f"Section: "
                    f"{item.section}"
                )

                print(
                    f"Date: "
                    f"{item.published_at}"
                )

                print(
                    f"Evidence ID: "
                    f"{item.evidence_id}"
                )

                print(
                    f"\n{item.text[:1200]}"
                )

    finally:

        retriever.close()


if __name__ == "__main__":
    main()
