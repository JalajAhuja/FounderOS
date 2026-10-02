import json
from pathlib import Path
from datetime import datetime, timedelta


# ============================================================
# CONFIG
# ============================================================

SUBMISSIONS_DIR = Path(
    "data/01_raw/sec/metadata/submissions"
)

FILINGS_DIR = Path(
    "data/01_raw/sec/metadata/filings"
)

TARGET_FORMS = {
    "10-K",
    "10-Q",
    "8-K"
}

YEARS_BACK = 3


# ============================================================
# EXTRACT FILINGS
# ============================================================

def extract_filings(
    submission_data,
    cutoff_date
):

    recent = (
        submission_data[
            "filings"
        ][
            "recent"
        ]
    )

    filings = []

    for i, form in enumerate(
        recent["form"]
    ):

        if form not in TARGET_FORMS:
            continue

        filing_date = (
            recent[
                "filingDate"
            ][i]
        )

        # ----------------------------------------------------
        # Date filtering
        # ----------------------------------------------------

        if filing_date:

            filing_datetime = (
                datetime.strptime(
                    filing_date,
                    "%Y-%m-%d"
                )
            )

            if filing_datetime < cutoff_date:
                continue

        # ----------------------------------------------------
        # Extract metadata
        # ----------------------------------------------------

        filing = {

            "accession_number":
                recent[
                    "accessionNumber"
                ][i],

            "filing_date":
                filing_date,

            "report_date":
                recent[
                    "reportDate"
                ][i],

            "form":
                form,

            "primary_document":
                recent[
                    "primaryDocument"
                ][i],

            "primary_doc_description":
                recent[
                    "primaryDocDescription"
                ][i],

            "file_number":
                recent[
                    "fileNumber"
                ][i],

            "items":
                recent[
                    "items"
                ][i],

            "is_xbrl":
                recent[
                    "isXBRL"
                ][i]
        }

        filings.append(
            filing
        )

    return filings


# ============================================================
# PROCESS ONE COMPANY
# ============================================================

def process_company(
    submission_file
):

    ticker = (
        submission_file
        .stem
        .upper()
    )

    print(
        f"Processing {ticker}"
    )

    with open(
        submission_file,
        encoding="utf-8"
    ) as f:

        submission_data = (
            json.load(f)
        )

    cutoff_date = (
        datetime.now()
        - timedelta(
            days=365 * YEARS_BACK
        )
    )

    filings = extract_filings(
        submission_data,
        cutoff_date
    )

    output_file = (
        FILINGS_DIR /
        f"{ticker}_filings.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            filings,
            f,
            indent=2
        )

    print(
        f"  Found {len(filings)} filings"
    )

    return len(filings)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - Filing Selection")
    print("=" * 60)

    FILINGS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    submission_files = sorted(
        SUBMISSIONS_DIR.glob(
            "*.json"
        )
    )

    total = 0

    for file in submission_files:

        total += process_company(
            file
        )

    print()
    print("=" * 60)
    print(
        f"Total selected filings: {total}"
    )
    print("=" * 60)


if __name__ == "__main__":

    main()