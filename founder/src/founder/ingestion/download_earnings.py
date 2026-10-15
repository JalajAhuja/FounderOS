import json
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/01_raw/earnings/transcripts/part-0.parquet"
)

OUTPUT_DIR = Path(
    "data/01_raw/earnings/transcripts"
)

TARGET_TICKERS = {
    "MSFT",
    "CRM",
    "NOW",
    "ADBE",
    "SHOP",
    "SNOW",
    "DDOG",
    "PLTR",
    "NVDA",
    "AMZN"
}


# ============================================================
# HELPERS
# ============================================================

def to_json_safe(value):
    """Recursively convert numpy/pandas objects into plain JSON-serializable types."""

    if isinstance(value, np.ndarray):
        return [to_json_safe(item) for item in value.tolist()]

    if isinstance(value, (np.generic,)):
        return value.item()

    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]

    return value


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - Earnings Call Downloader")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        f"Loading local parquet file: "
        f"{INPUT_FILE}",
        flush=True,
    )

    df = pd.read_parquet(INPUT_FILE)

    count = 0
    scanned = 0

    for row in df.to_dict("records"):

        scanned += 1
        if scanned % 1000 == 0:
            print(
                f"Scanned {scanned} rows; saved {count} matching earnings calls...",
                flush=True,
            )

        ticker = (
            str(
                row.get(
                    "symbol",
                    ""
                )
            )
            .upper()
        )

        if ticker not in TARGET_TICKERS:
            continue

        year = row.get(
            "year"
        )

        quarter = row.get(
            "quarter"
        )

        date = row.get(
            "date"
        )

        content = row.get(
            "content"
        )

        if not content:
            continue

        record = {

            "source":
                "earnings_call",

            "ticker":
                ticker,

            "company":
                row.get(
                    "company_name"
                ),

            "year":
                year,

            "quarter":
                quarter,

            "date":
                date,

            "text":
                content,

            "structured_content":
                row.get(
                    "structured_content"
                )
        }

        record = to_json_safe(record)

        filename = (
            f"{ticker}_"
            f"{year}_Q{quarter}.json"
        )

        output_file = (
            OUTPUT_DIR /
            filename
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                record,
                f,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        count += 1

        if count % 25 == 0:

            print(
                f"Downloaded {count} "
                f"earnings calls...",
                flush=True,
            )

    print()
    print("=" * 60)

    print(
        f"Earnings calls saved: "
        f"{count}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
