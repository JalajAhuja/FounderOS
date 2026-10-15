import json
from pathlib import Path

from datasets import load_dataset

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


def download_earnings():

    dataset = load_dataset(
        "lamini/earnings-calls-qa",
        split="train",
        streaming=True
    )

    output_dir = Path("data/01_raw/earnings/lamini")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        "earnings_filtered.jsonl"
    )

    count = 0

    with open(output_file, "w") as f:

        for row in dataset:

            ticker = row.get("ticker")

            if ticker not in TARGET_TICKERS:
                continue

            record = {
                "ticker": ticker,
                "date": row.get("date"),
                "quarter": row.get("q"),
                "question": row.get("question"),
                "answer": row.get("answer"),
                "transcript": row.get("transcript")
            }

            f.write(
                json.dumps(record) + "\n"
            )

            count += 1

            if count % 1000 == 0:
                print(f"Saved {count} records")


if __name__ == "__main__":
    download_earnings()
