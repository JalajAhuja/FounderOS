import json
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

RAW_FACTS_DIR = Path(
    "data/01_raw/sec/facts"
)

OUTPUT_DIR = Path(
    "data/03_primary"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "facts.jsonl"
)


# ============================================================
# IMPORTANT FINANCIAL CONCEPTS
# ============================================================

TARGET_CONCEPTS = {

    "Revenues": "revenue",

    "RevenueFromContractWithCustomerExcludingAssessedTax":
        "revenue",

    "SalesRevenueNet":
        "revenue",

    "NetIncomeLoss":
        "net_income",

    "OperatingIncomeLoss":
        "operating_income",

    "GrossProfit":
        "gross_profit",

    "Assets":
        "assets",

    "Liabilities":
        "liabilities",

    "StockholdersEquity":
        "equity",

    "CashAndCashEquivalentsAtCarryingValue":
        "cash",

    "LongTermDebtNoncurrent":
        "long_term_debt",

    "EarningsPerShareBasic":
        "eps_basic",

    "EarningsPerShareDiluted":
        "eps_diluted",

    "WeightedAverageNumberOfSharesOutstandingBasic":
        "shares_basic",

    "WeightedAverageNumberOfDilutedSharesOutstanding":
        "shares_diluted"
}


# ============================================================
# PROCESS ONE COMPANY
# ============================================================

def process_company(
    file
):

    ticker = (
        file.stem
        .upper()
    )

    print(
        f"Processing facts: "
        f"{ticker}"
    )

    with open(
        file,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    facts = data.get(
        "facts",
        {}
    )

    us_gaap = facts.get(
        "us-gaap",
        {}
    )

    records = []

    for concept_name, canonical_name in (
        TARGET_CONCEPTS.items()
    ):

        if concept_name not in us_gaap:
            continue

        concept = us_gaap[
            concept_name
        ]

        units = concept.get(
            "units",
            {}
        )

        for unit, values in units.items():

            for value in values:

                record = {

                    "fact_id":
                        (
                            f"{ticker}_"
                            f"{canonical_name}_"
                            f"{value.get('fy')}_"
                            f"{value.get('fp')}_"
                            f"{value.get('end')}"
                        ),

                    "ticker":
                        ticker,

                    "fact":
                        canonical_name,

                    "concept":
                        concept_name,

                    "value":
                        value.get(
                            "val"
                        ),

                    "unit":
                        unit,

                    "start":
                        value.get(
                            "start"
                        ),

                    "end":
                        value.get(
                            "end"
                        ),

                    "fiscal_year":
                        value.get(
                            "fy"
                        ),

                    "fiscal_period":
                        value.get(
                            "fp"
                        ),

                    "form":
                        value.get(
                            "form"
                        ),

                    "filed":
                        value.get(
                            "filed"
                        ),

                    "frame":
                        value.get(
                            "frame"
                        ),

                    "accn":
                        value.get(
                            "accn"
                        )
                }

                records.append(
                    record
                )

    return records


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - Building Financial Facts")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = list(
        RAW_FACTS_DIR.glob(
            "*.json"
        )
    )

    total = 0

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as output:

        for file in files:

            records = process_company(
                file
            )

            for record in records:

                output.write(
                    json.dumps(
                        record
                    )
                    + "\n"
                )

                total += 1

    print()
    print(
        f"Facts written: {total}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
