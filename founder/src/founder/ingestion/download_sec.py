import json
from pathlib import Path

import requests


# ============================================================
# CONFIG
# ============================================================

HEADERS = {
    "User-Agent": "FounderOS Research Project oneandonlyjalajahuja@gmail.com"
}

URL = "https://www.sec.gov/files/company_tickers.json"

OUTPUT_DIR = Path(
    "data/01_raw/sec/metadata"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "company_tickers.json"
)


# ============================================================
# DOWNLOAD
# ============================================================

def download_company_tickers():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Downloading SEC company ticker mapping...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )

    print(
        f"Saved {len(data)} companies"
    )

    print(
        f"File: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    download_company_tickers()