import csv
import json
import time
from pathlib import Path
from xml.etree import ElementTree

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


# ============================================================
# CONFIG
# ============================================================
#
# GDELT's doc API throttles very aggressively (persistent 429s
# regardless of delay, especially from cloud/shared IPs), so we
# use the Google News RSS search feed instead. It needs no API
# key and tolerates much higher request rates.

COMPANIES_FILE = Path(
    "data/companies.csv"
)

OUTPUT_DIR = Path(
    "data/01_raw/news"
)

API_URL = (
    "https://news.google.com/rss/search"
)

MAX_RECORDS = 75

TIMESPAN = "365d"

REQUEST_DELAY = 2

MAX_ATTEMPTS = 5


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
# QUERY GOOGLE NEWS
# ============================================================

@retry(
    reraise=True,
    stop=stop_after_attempt(MAX_ATTEMPTS),
    wait=wait_exponential(multiplier=5, min=5, max=120),
    retry=retry_if_exception_type(
        (requests.exceptions.HTTPError, ElementTree.ParseError)
    ),
)
def search_company(
    ticker,
    company
):

    # Search exact company name and ticker.
    #
    # We don't want every article containing
    # the ticker as an unrelated word.

    query = (
        f'"{company}" OR "{ticker}" when:{TIMESPAN}'
    )

    params = {

        "q":
            query,

        "hl":
            "en-US",

        "gl":
            "US",

        "ceid":
            "US:en",
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=60,
        headers={
            "User-Agent":
                "Mozilla/5.0 (compatible; FounderOS/1.0)"
        },
    )

    response.raise_for_status()

    root = ElementTree.fromstring(response.content)

    articles = []

    for item in root.findall("./channel/item")[:MAX_RECORDS]:

        articles.append({

            "title":
                item.findtext("title"),

            "url":
                item.findtext("link"),

            "seendate":
                item.findtext("pubDate"),

            "source":
                item.findtext("source"),
        })

    return {
        "articles":
            articles
    }



# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - Google News RSS Ingestion")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    companies = load_companies()

    for company in companies:

        ticker = (
            company["ticker"]
            .upper()
        )

        name = company[
            "company"
        ]

        print(
            f"\nSearching news: "
            f"{ticker}"
        )

        try:

            data = search_company(
                ticker,
                name
            )

            output_file = (
                OUTPUT_DIR
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
                    indent=2,
                    ensure_ascii=False
                )

            articles = (
                data.get(
                    "articles",
                    []
                )
            )

            print(
                f"Articles found: "
                f"{len(articles)}"
            )

        except Exception as e:

            print(
                f"ERROR: {e}"
            )

        time.sleep(REQUEST_DELAY)

    print()
    print("=" * 60)
    print("News ingestion complete")
    print("=" * 60)


if __name__ == "__main__":
    main()