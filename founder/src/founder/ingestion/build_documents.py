import json
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

CLEAN_DIR = Path(
    "data/01_raw/sec/clean"
)

FILINGS_DIR = Path(
    "data/01_raw/sec/metadata/filings"
)

OUTPUT_DIR = Path(
    "data/03_primary"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "documents.jsonl"
)


# ============================================================
# LOAD FILING METADATA
# ============================================================

def load_filing_metadata():

    metadata = {}

    for file in FILINGS_DIR.glob(
        "*_filings.json"
    ):

        ticker = (
            file.stem
            .replace(
                "_filings",
                ""
            )
            .upper()
        )

        with open(
            file,
            encoding="utf-8"
        ) as f:

            filings = json.load(f)

        for filing in filings:

            primary_document = (
                filing.get(
                    "primary_document"
                )
            )

            if not primary_document:
                continue

            key = (
                ticker,
                primary_document
            )

            metadata[key] = filing

    return metadata


# ============================================================
# BUILD DOCUMENT
# ============================================================

def build_document(
    text_file,
    metadata
):

    relative = (
        text_file.relative_to(
            CLEAN_DIR
        )
    )

    # Expected:
    #
    # ticker/
    # form/
    # year/
    # filename.txt

    if len(relative.parts) != 4:

        raise ValueError(
            f"Unexpected file structure: "
            f"{relative}"
        )

    ticker = relative.parts[0]
    form = relative.parts[1]
    year = relative.parts[2]

    original_filename = (
        text_file.stem
        + ".htm"
    )

    key = (
        ticker,
        original_filename
    )

    filing = metadata.get(
        key
    )

    if filing is None:

        raise ValueError(
            f"No SEC metadata found for "
            f"{ticker} / "
            f"{original_filename}"
        )

    text = text_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    if not text.strip():

        raise ValueError(
            f"Empty document: "
            f"{text_file}"
        )

    accession = filing[
        "accession_number"
    ]

    document_id = (
        f"sec_"
        f"{ticker}_"
        f"{form}_"
        f"{year}_"
        f"{text_file.stem}"
    )

    # Reconstruct SEC URL
    cik = None

    document = {

        "document_id":
            document_id,

        "source":
            "SEC",

        "ticker":
            ticker,

        "title":
            f"{ticker} {form} {year}",

        "text":
            text,

        "published_at":
            filing.get(
                "filing_date"
            ),

        "period_end":
            filing.get(
                "report_date"
            ),

        "document_type":
            form,

        "metadata": {

            "accession_number":
                accession,

            "primary_document":
                filing.get(
                    "primary_document"
                ),

            "primary_doc_description":
                filing.get(
                    "primary_doc_description"
                ),

            "file_number":
                filing.get(
                    "file_number"
                ),

            "is_xbrl":
                filing.get(
                    "is_xbrl"
                ),

            "source_type":
                "regulatory_filing",

            "local_path":
                str(text_file)
        }
    }

    return document


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - Building Canonical Documents")
    print("=" * 60)

    if not CLEAN_DIR.exists():

        print(
            f"ERROR: Clean directory does not exist:"
        )

        print(
            CLEAN_DIR
        )

        print(
            "\nRun clean_filings.py first."
        )

        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "Loading SEC filing metadata..."
    )

    metadata = (
        load_filing_metadata()
    )

    print(
        f"Metadata records: "
        f"{len(metadata)}"
    )

    text_files = list(
        CLEAN_DIR.rglob(
            "*.txt"
        )
    )

    print(
        f"Clean documents found: "
        f"{len(text_files)}"
    )

    if not text_files:

        print()
        print(
            "ERROR: No .txt files found."
        )

        print(
            "Run clean_filings.py first."
        )

        return

    successful = 0
    failed = 0

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as output:

        for text_file in text_files:

            try:

                document = (
                    build_document(
                        text_file,
                        metadata
                    )
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
                    f"ERROR: {text_file}"
                )

                print(
                    f"       {e}"
                )

    print()
    print("=" * 60)
    print("Canonical dataset complete")
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