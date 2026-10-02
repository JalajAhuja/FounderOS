"""Rebuild primary dataset from raw data."""

import json
from pathlib import Path


def rebuild_dataset():
    """Rebuild documents.jsonl, facts.jsonl, earnings.jsonl, news.jsonl."""

    raw_path = Path("data/01_raw")

    primary_path = Path("data/03_primary")

    primary_path.mkdir(parents=True, exist_ok=True)

    print("Rebuilding primary dataset...")

    # Check for raw data subdirectories
    if (raw_path / "sec" / "documents").exists():

        documents = []

        for doc_file in (raw_path / "sec" / "documents").glob("*.json"):

            with open(doc_file) as f:
                documents.append(json.load(f))

        with open(primary_path / "documents.jsonl", "w") as f:

            for doc in documents:
                f.write(json.dumps(doc) + "\n")

        print(f"[OK] Created documents.jsonl ({len(documents)} items)")

    # Facts
    if (raw_path / "sec" / "facts").exists():

        facts = []

        for fact_file in (raw_path / "sec" / "facts").glob("*.json"):

            with open(fact_file) as f:
                facts.append(json.load(f))

        with open(primary_path / "facts.jsonl", "w") as f:

            for fact in facts:
                f.write(json.dumps(fact) + "\n")

        print(f"[OK] Created facts.jsonl ({len(facts)} items)")

    # Earnings
    if (raw_path / "earnings" / "transcripts").exists():

        earnings = []

        for earn_file in (raw_path / "earnings" / "transcripts").glob("*.json"):

            with open(earn_file) as f:
                earnings.append(json.load(f))

        with open(primary_path / "earnings.jsonl", "w") as f:

            for earn in earnings:
                f.write(json.dumps(earn) + "\n")

        print(f"[OK] Created earnings.jsonl ({len(earnings)} items)")

    # News
    if (raw_path / "news").exists():

        news = []

        for news_file in (raw_path / "news").glob("*.json"):

            with open(news_file) as f:
                news.append(json.load(f))

        with open(primary_path / "news.jsonl", "w") as f:

            for n in news:
                f.write(json.dumps(n) + "\n")

        print(f"[OK] Created news.jsonl ({len(news)} items)")


if __name__ == "__main__":
    rebuild_dataset()
