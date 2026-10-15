import json
import time
from pathlib import Path

import requests

# ============================================================
# CONFIG
# ============================================================

HEADERS = {
    "User-Agent": "FounderOS Research Project oneandonlyjalajahuja@gmail.com"
}

FILINGS_DIR = Path(
    "data/01_raw/sec/metadata/filings"
)

DOCUMENTS_DIR = Path(
    "data/01_raw/sec/documents"
)


# ============================================================
# BUILD SEC ARCHIVE URL
# ============================================================

def build_filing_url(
    cik,
    accession_number,
    primary_document
):

    # CIK without leading zeros
    cik_clean = str(
        int(cik)
    )

    # SEC archive removes dashes
    accession_clean = (
        accession_number
        .replace("-", "")
    )

    url = (
        "https://www.sec.gov/"
        "Archives/edgar/data/"
        f"{cik_clean}/"
        f"{accession_clean}/"
        f"{primary_document}"
    )

    return url


# ============================================================
# GET CIK FROM SUBMISSION
# ============================================================

def get_cik(
    ticker
):

    submission_file = (
        Path(
            "data/01_raw/sec/"
            "metadata/submissions"
        )
        /
        f"{ticker}.json"
    )

    with open(
        submission_file,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data["cik"]


# ============================================================
# DOWNLOAD ONE FILING
# ============================================================

def download_filing(
    ticker,
    cik,
    filing
):

    form = filing[
        "form"
    ]

    accession = filing[
        "accession_number"
    ]

    primary_document = filing[
        "primary_document"
    ]

    filing_date = filing[
        "filing_date"
    ]

    year = filing_date[
        :4
    ]

    output_dir = (
        DOCUMENTS_DIR
        / ticker
        / form
        / year
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / primary_document
    )

    # --------------------------------------------------------
    # Skip if already downloaded
    # --------------------------------------------------------

    if output_file.exists():

        print(
            f"  Already exists: "
            f"{output_file}"
        )

        return

    url = build_filing_url(
        cik,
        accession,
        primary_document
    )

    print(
        f"  Downloading {form}: "
        f"{primary_document}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    output_file.write_bytes(
        response.content
    )

    # Save URL/provenance
    metadata_file = (
        output_dir /
        f"{primary_document}.metadata.json"
    )

    metadata = {
        "ticker": ticker,
        "cik": cik,
        "form": form,
        "filing_date": filing_date,
        "report_date": filing[
            "report_date"
        ],
        "accession_number":
            accession,
        "primary_document":
            primary_document,
        "source_url": url
    }

    with open(
        metadata_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2
        )

    time.sleep(0.25)


# ============================================================
# PROCESS COMPANY
# ============================================================

def process_company(
    filings_file
):

    ticker = (
        filings_file
        .stem
        .replace(
            "_filings",
            ""
        )
        .upper()
    )

    print()
    print(
        f"========== {ticker} =========="
    )

    with open(
        filings_file,
        encoding="utf-8"
    ) as f:

        filings = json.load(f)

    cik = get_cik(
        ticker
    )

    for filing in filings:

        try:

            download_filing(
                ticker,
                cik,
                filing
            )

        except requests.RequestException as e:

            print(
                f"  ERROR: {e}"
            )

        except Exception as e:

            print(
                f"  ERROR: {e}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - SEC Filing Downloader")
    print("=" * 60)

    filing_files = sorted(
        FILINGS_DIR.glob(
            "*_filings.json"
        )
    )

    print(
        f"Companies: "
        f"{len(filing_files)}"
    )

    for filing_file in filing_files:

        process_company(
            filing_file
        )

    print()
    print("=" * 60)
    print("SEC document download complete")
    print("=" * 60)


if __name__ == "__main__":

    main()
