import json
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_DIR = Path(
    "data/01_raw/earnings/transcripts"
)

OUTPUT_DIR = Path(
    "data/03_primary"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "earnings.jsonl"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - Building Earnings Corpus")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = sorted(
        INPUT_DIR.glob(
            "*.json"
        )
    )

    count = 0

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as output:

        for file in files:

            with open(
                file,
                encoding="utf-8"
            ) as f:

                record = json.load(f)

            ticker = record[
                "ticker"
            ]

            year = record[
                "year"
            ]

            quarter = record[
                "quarter"
            ]

            document_id = (
                f"earnings_"
                f"{ticker}_"
                f"{year}_"
                f"Q{quarter}"
            )

            document = {

                "document_id":
                    document_id,

                "source":
                    "earnings_call",

                "ticker":
                    ticker,

                "title":
                    (
                        f"{ticker} "
                        f"Q{quarter} "
                        f"{year} "
                        f"Earnings Call"
                    ),

                "text":
                    record["text"],

                "published_at":
                    record["date"],

                "document_type":
                    "earnings_call",

                "metadata": {

                    "company":
                        record.get(
                            "company"
                        ),

                    "year":
                        year,

                    "quarter":
                        quarter,

                    "structured_content":
                        record.get(
                            "structured_content"
                        )
                }
            }

            output.write(
                json.dumps(
                    document,
                    ensure_ascii=False
                )
                + "\n"
            )

            count += 1

    print()
    print(
        f"Earnings documents: "
        f"{count}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()