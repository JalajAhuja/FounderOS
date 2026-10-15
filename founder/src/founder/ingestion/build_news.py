import json
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

INPUT_DIR = Path(
    "data/01_raw/news"
)

OUTPUT_DIR = Path(
    "data/03_primary"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "news.jsonl"
)


# ============================================================
# HELPERS
# ============================================================

def parse_year(value):

    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%a, %d %b %Y %H:%M:%S %Z"
        ).year
    except ValueError:
        return None


def build_document(
    article,
    ticker,
    article_index
):

    title = (
        article.get(
            "title"
        )
        or ""
    ).strip()

    if not title:
        raise ValueError(
            "Article title is empty"
        )

    published_at = article.get(
        "seendate"
    )

    document_id = (
        f"news_"
        f"{ticker}_"
        f"{article_index:04d}"
    )

    return {

        "document_id":
            document_id,

        "source":
            "news",

        "ticker":
            ticker,

        "title":
            title,

        "text":
            title,

        "published_at":
            published_at,

        "document_type":
            "news",

        "metadata": {

            "url":
                article.get(
                    "url"
                ),

            "domain":
                article.get(
                    "source"
                ),

            "year":
                parse_year(
                    published_at
                ),
        }
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - Building News Corpus")
    print("=" * 60)

    if not INPUT_DIR.exists():

        print(
            f"ERROR: News directory does not exist: "
            f"{INPUT_DIR}"
        )

        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = sorted(
        INPUT_DIR.glob(
            "*.json"
        )
    )

    successful = 0
    failed = 0

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as output:

        for file in files:

            ticker = file.stem.upper()

            try:

                with open(
                    file,
                    encoding="utf-8"
                ) as f:

                    record = json.load(f)

                articles = record.get(
                    "articles",
                    []
                )

                for article_index, article in enumerate(
                    articles,
                    start=1
                ):

                    document = build_document(
                        article,
                        ticker,
                        article_index
                    )

                    output.write(
                        json.dumps(
                            document,
                            ensure_ascii=False
                        )
                        + "\n"
                    )

                    successful += 1

            except Exception as e:

                failed += 1

                print()
                print(
                    f"ERROR: {file}"
                )
                print(
                    f"       {e}"
                )

    print()
    print("=" * 60)
    print("News corpus complete")
    print("=" * 60)
    print(
        f"Successful: {successful}"
    )
    print(
        f"Failed:     {failed}"
    )
    print(
        f"Output:     {OUTPUT_FILE}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
