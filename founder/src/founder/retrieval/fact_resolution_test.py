"""Manual fact resolution test (Step 21)."""

from founder.storage.period_mapping import resolve_fiscal_period


def main():

    print("\n== Fiscal Period Resolution ==\n")

    test_cases = [
        ("MSFT", "2025-06-30", "FY2025-Q4"),
        ("MSFT", "2025-05-31", "2025-Q4"),
        ("AAPL", "2025-09-30", "2025-Q1"),
        ("GOOGL", "2025-12-31", "2025-Q4"),
        ("unknown_ticker", "2025-06-15", "2025-Q2"),
    ]

    for ticker, date, expected in test_cases:

        result = resolve_fiscal_period(ticker, date)

        print(
            f"{ticker:15s} | {date} | "
            f"{result['canonical']:12s} "
            f"(basis={result['basis']:15s})"
        )

    print("\nNote: Full SEC fiscal calendar integration is Step 33.")


if __name__ == "__main__":
    main()
