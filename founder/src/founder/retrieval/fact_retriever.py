import json
import re
from pathlib import Path


FACTS_FILE = Path(
    "data/03_primary/facts.jsonl"
)


# ============================================================
# CONCEPT ALIASES
# ============================================================

CONCEPT_ALIASES = {

    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
    ],

    "net income": [
        "NetIncomeLoss",
    ],

    "operating income": [
        "OperatingIncomeLoss",
    ],

    "gross profit": [
        "GrossProfit",
    ],

    "assets": [
        "Assets",
    ],

    "liabilities": [
        "Liabilities",
    ],

    "equity": [
        "StockholdersEquity",
    ],

    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
    ],

    "long term debt": [
        "LongTermDebtNoncurrent",
    ],

    "eps": [
        "EarningsPerShareBasic",
        "EarningsPerShareDiluted",
    ],
}


# ============================================================
# HELPERS
# ============================================================

def normalize(value):

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value).lower(),
    ).strip()


def infer_concepts(query):

    normalized = normalize(
        query
    )

    concepts = []

    for keyword, candidates in (
        CONCEPT_ALIASES.items()
    ):

        if keyword in normalized:

            concepts.extend(
                candidates
            )

    return list(
        dict.fromkeys(concepts)
    )


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

        if re.search(
            pattern,
            query_upper,
        ):
            return ticker.upper()

    return None


# ============================================================
# RETRIEVER
# ============================================================

class FactRetriever:

    def __init__(self):

        self.facts = []

        if not FACTS_FILE.exists():

            print(
                f"WARNING: facts file not found: "
                f"{FACTS_FILE}"
            )

            return

        with open(
            FACTS_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                try:

                    self.facts.append(
                        json.loads(line)
                    )

                except json.JSONDecodeError:
                    continue

        self.tickers = sorted(
            {
                str(
                    fact.get(
                        "ticker",
                        ""
                    )
                ).upper()

                for fact in self.facts

                if fact.get(
                    "ticker"
                )
            }
        )

        print(
            f"Loaded {len(self.facts):,} XBRL facts."
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query,
        ticker=None,
        top_k=10,
    ):

        concepts = infer_concepts(
            query
        )

        if ticker is None:

            ticker = infer_ticker(
                query,
                self.tickers,
            )

        candidates = []

        for fact in self.facts:

            fact_ticker = str(
                fact.get(
                    "ticker",
                    ""
                )
            ).upper()

            if ticker:

                if fact_ticker != ticker.upper():
                    continue

            concept = str(
                fact.get(
                    "concept",
                    ""
                )
            )

            fact_name = str(
                fact.get(
                    "fact",
                    ""
                )
            )

            # If query maps to concepts,
            # only keep matching concepts.
            if concepts:

                if (
                    concept not in concepts
                    and fact_name not in concepts
                ):
                    continue

            candidates.append(
                fact
            )

        # ----------------------------------------------------
        # Sort by most recent filing
        # ----------------------------------------------------

        def sort_key(fact):

            return (
                str(
                    fact.get(
                        "end",
                        ""
                    )
                ),
                str(
                    fact.get(
                        "filed",
                        ""
                    )
                ),
            )

        candidates.sort(
            key=sort_key,
            reverse=True,
        )

        return candidates[:top_k]