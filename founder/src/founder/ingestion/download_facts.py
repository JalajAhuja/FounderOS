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

RAW_FACTS_DIR = Path(
    "data/01_raw/sec/facts"
)


# ============================================================
# LOAD COMPANIES
# ============================================================

def load_companies():

    with open(
        COMPANIES_FILE,
        newline="",
        encoding="utf-8"
    ) as f:

        return list(
            csv.DictReader(f)
        )


# ============================================================
# BUILD TICKER -> CIK
# ============================================================

def build_ticker_map():

    with open(
        TICKER_FILE,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    result = {}

    for item in data.values():

        ticker = (
            item["ticker"]
            .upper()
        )

        result[ticker] = (
            str(
                item["cik_str"]
            ).zfill(10)
        )

    return result


# ============================================================
# DOWNLOAD COMPANY FACTS
# ============================================================

def download_company_facts(
    cik
):

    url = (
        "https://data.sec.gov/"
        f"api/xbrl/companyfacts/"
        f"CIK{cik}.json"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - SEC XBRL Facts")
    print("=" * 60)

    RAW_FACTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    companies = load_companies()
    ticker_map = build_ticker_map()

    for company in companies:

        ticker = (
            company["ticker"]
            .upper()
        )

        print(
            f"\nDownloading facts: "
            f"{ticker}"
        )

        if ticker not in ticker_map:

            print(
                f"CIK not found: {ticker}"
            )

            continue

        cik = ticker_map[ticker]

        try:

            data = download_company_facts(
                cik
            )

            output_file = (
                RAW_FACTS_DIR
                / f"{ticker}.json"
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

        except Exception as e:

            print(
                f"ERROR: {ticker}"
            )

            print(e)

        time.sleep(0.25)

    print()
    print("=" * 60)
    print("XBRL download complete")
    print("=" * 60)


if __name__ == "__main__":
    main()