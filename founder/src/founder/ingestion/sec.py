import csv
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

COMPANIES_FILE = Path(
    "data/companies.csv"
)

TICKER_FILE = Path(
    "data/01_raw/sec/metadata/company_tickers.json"
)

SUBMISSIONS_DIR = Path(
    "data/01_raw/sec/metadata/submissions"
)


# ============================================================
# LOAD TARGET COMPANIES
# ============================================================

def load_target_companies():

    companies = []

    with open(
        COMPANIES_FILE,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            companies.append(row)

    return companies


# ============================================================
# BUILD TICKER -> CIK MAP
# ============================================================

def build_ticker_map():

    with open(
        TICKER_FILE,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    ticker_map = {}

    for item in data.values():

        ticker = item["ticker"].upper()

        ticker_map[ticker] = {

            "cik":
                str(
                    item["cik_str"]
                ).zfill(10),

            "company_name":
                item["title"]
        }

    return ticker_map


# ============================================================
# GET SEC SUBMISSIONS
# ============================================================

def get_submissions(cik):

    url = (
        "https://data.sec.gov/"
        f"submissions/CIK{cik}.json"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - SEC Submission Downloader")
    print("=" * 60)

    SUBMISSIONS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    companies = (
        load_target_companies()
    )

    ticker_map = (
        build_ticker_map()
    )

    print(
        f"Companies to process: "
        f"{len(companies)}"
    )

    for company in companies:

        ticker = (
            company["ticker"]
            .upper()
        )

        print()
        print(
            f"Downloading {ticker}..."
        )

        if ticker not in ticker_map:

            print(
                f"ERROR: {ticker} "
                f"not found in SEC mapping"
            )

            continue

        cik = ticker_map[
            ticker
        ][
            "cik"
        ]

        try:

            data = get_submissions(
                cik
            )

            output_file = (
                SUBMISSIONS_DIR /
                f"{ticker}.json"
            )

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2
                )

            print(
                f"Saved: {output_file}"
            )

        except requests.RequestException as e:

            print(
                f"ERROR for {ticker}: {e}"
            )

        # Don't hammer SEC
        time.sleep(0.25)

    print()
    print("=" * 60)
    print("SEC submissions download complete")
    print("=" * 60)


if __name__ == "__main__":

    main()