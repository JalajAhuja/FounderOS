"""Interactive REPL for the FounderOS LangGraph agent.

Mirrors `founder.retrieval.test_unified` but drives the compiled agent
graph instead of calling `UnifiedRetriever` directly.
"""

import uuid

from founder.agent.graph import get_app
from founder.agent.state import initial_state
from founder.agent.tools import get_bundle


def run_query(query: str) -> dict:

    app = get_app()

    state = app.invoke(
        initial_state(
            query,
            trace_id=str(uuid.uuid4()),
        )
    )

    return {
        "answer": state.get("answer"),
        "evidence": state.get("evidence"),
        "claims": state.get("claims"),
        "citations": state.get("citations"),
        "limitations": state.get("limitations"),
        "retrieval_plan": state.get("query_plan"),
        "sufficiency": state.get("sufficiency"),
        "contradictions": state.get("contradictions"),
        "temporal_context": state.get("temporal_context"),
        "errors": state.get("errors"),
    }


def main():

    print(
        "\nInitializing FounderOS agent..."
    )

    try:

        get_bundle()

    except Exception as error:

        print(
            f"FATAL: could not initialize retrievers: {error}"
        )

        return

    print("\n" + "=" * 70)
    print("FounderOS Agent")
    print("=" * 70)

    try:

        while True:

            query = input("\nFounderOS> ").strip()

            if query.lower() in {"exit", "quit", "q"}:
                break

            if not query:
                continue

            result = run_query(query)

            print("\n" + "-" * 70)
            print(f"Answer:\n{result['answer']}")
            print("-" * 70)

            print(f"Evidence used: {len(result['evidence'] or [])}")

            for citation in result["citations"] or []:

                print(
                    f"  [{citation['citation_id']}] "
                    f"{citation['source']} "
                    f"({citation['date']}) "
                    f"{citation['evidence_id']}"
                )

            if result["limitations"]:
                print(f"\nLimitations: {result['limitations']}")

            if result["errors"]:
                print(f"\nErrors: {result['errors']}")

    finally:

        get_bundle().close()


if __name__ == "__main__":
    main()
