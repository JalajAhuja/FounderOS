import json
import re
from pathlib import Path


NEWS_FILE = Path(
    "data/03_primary/news.jsonl"
)


def normalize(value):

    return re.sub(
        r"[^a-z0-9 ]+",
        " ",
        str(value).lower(),
    ).strip()


def infer_ticker(
    query,
    known_tickers=None,
):

    if not known_tickers:
        return None

    query_upper = query.upper()

    for ticker in known_tickers:

        pattern = (
            rf"\b{re.escape(ticker.upper())}\b"
        )

        if re.search(pattern, query_upper):
            return ticker.upper()

    return None


class NewsRetriever:
    """Lightweight retriever over `data/03_primary/news.jsonl`.

    Intentionally simple keyword/ticker matching. Event extraction, source
    licensing checks, and richer causal-context handling are hardened in
    Step 31 (External Event / News Quality Hardening).
    """

    def __init__(self):

        self.articles = []

        if not NEWS_FILE.exists():

            print(
                f"WARNING: news file not found: {NEWS_FILE}"
            )

            return

        with open(
            NEWS_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                try:
                    self.articles.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        self.tickers = sorted(
            {
                str(article.get("ticker", "")).upper()
                for article in self.articles
                if article.get("ticker")
            }
        )

        print(f"Loaded {len(self.articles):,} news articles.")

    def search(
        self,
        query,
        ticker=None,
        top_k=10,
    ):

        if ticker is None:
            ticker = infer_ticker(query, self.tickers)

        query_terms = [
            term
            for term in normalize(query).split()
            if len(term) >= 4
        ]

        candidates = []

        for article in self.articles:

            article_ticker = str(
                article.get("ticker", "")
            ).upper()

            if ticker and article_ticker != ticker.upper():
                continue

            title_normalized = normalize(
                article.get("title", "")
            )

            if query_terms:

                if not any(
                    term in title_normalized
                    for term in query_terms
                ):
                    continue

            candidates.append(article)

        candidates.sort(
            key=lambda article: str(
                article.get("published_at", "")
            ),
            reverse=True,
        )

        return candidates[:top_k]
