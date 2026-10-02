"""Manual verification script for the Step 13 temporal graph helpers.

Run with:

    python -m founder.graph.timeline_test

Requires a running Neo4j instance populated by `founder.graph.write_graph`.
"""

from founder.graph.neo4j_client import Neo4jClient
from founder.graph.timeline import (
    compare_periods,
    find_new_relationships,
    find_removed_relationships,
    get_company_timeline,
    get_relationship_timeline,
)


def main():

    ticker = input("Ticker (e.g. MSFT): ").strip().upper()

    client = Neo4jClient()

    try:

        print("\n== get_company_timeline ==")

        for row in get_company_timeline(ticker, client=client)[:20]:

            print(
                f"{row['published_at']} | {row['source']} "
                f"--{row['relationship']}--> {row['target']} "
                f"(chunk={row['chunk_id']})"
            )

        print("\n== get_relationship_timeline (entity search) ==")

        entity_name = input(
            "Entity name to trace (e.g. a company/technology): "
        ).strip()

        if entity_name:

            for row in get_relationship_timeline(
                entity_name, client=client
            )[:20]:

                print(
                    f"{row['published_at']} | {row['source']} "
                    f"--{row['relationship']}--> {row['target']}"
                )

        print("\n== find_new_relationships (since 2025-01-01) ==")

        for row in find_new_relationships(
            ticker, "2025-01-01", client=client
        )[:20]:

            print(
                f"{row['source']} --{row['relationship']}--> "
                f"{row['target']} (first_seen={row['first_seen']})"
            )

        print("\n== find_removed_relationships (before 2025-01-01) ==")

        for row in find_removed_relationships(
            ticker, "2025-01-01", "2025-06-01", client=client
        )[:20]:

            print(
                f"{row['source']} --{row['relationship']}--> "
                f"{row['target']} (last_seen={row['last_seen']})"
            )

        print("\n== compare_periods (2025 H1 vs 2025 H2) ==")

        comparison = compare_periods(
            ticker,
            "2025-01-01",
            "2025-06-30",
            "2025-07-01",
            "2025-12-31",
            client=client,
        )

        print(f"Added: {comparison['added']}")
        print(f"Removed: {comparison['removed']}")
        print(f"Unchanged: {len(comparison['unchanged'])} relationships")

    finally:

        client.close()


if __name__ == "__main__":
    main()
