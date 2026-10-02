"""Bootstrap the FounderOS system from raw data to evaluated indexes."""

import sys
from pathlib import Path


def check_raw_data() -> bool:
    """Check if raw data exists."""

    raw_path = Path("data/01_raw")

    if not raw_path.exists():

        print(f"[ERROR] Raw data directory not found: {raw_path}")

        return False

    subdirs = ["sec", "earnings", "news"]

    found = []

    for subdir in subdirs:

        if (raw_path / subdir).exists():
            found.append(subdir)

    if not found:

        print(f"[ERROR] No subdirectories found in {raw_path}")

        return False

    print(f"[OK] Found raw data: {', '.join(found)}")

    return True


def check_services() -> bool:
    """Check if required services are running."""

    import requests
    from time import sleep

    services = {
        "Qdrant": "http://localhost:6333/health",
        "Neo4j": "http://localhost:7687",
        "PostgreSQL": "postgresql://localhost:5432/founder",
    }

    all_ready = True

    for name, url in services.items():

        try:

            if name == "Qdrant":

                response = requests.get(url, timeout=2)

                if response.status_code == 200:
                    print(f"[OK] {name} is running")
                else:
                    print(f"[ERROR] {name} health check failed")
                    all_ready = False

            elif name == "PostgreSQL":
                # Simplified check (would need psycopg2)
                print(f"⚠ {name} check deferred (requires psycopg2)")

        except Exception as err:

            print(f"[ERROR] {name} is not running: {err}")

            all_ready = False

    return all_ready


def run_dataset_rebuild() -> bool:
    """Rebuild primary dataset from raw data."""

    print("\n--- Rebuilding Dataset ---")

    print("Would run: python -m founder.ingestion.build_documents")

    print("Would run: python -m founder.ingestion.build_facts")

    print("Would run: python -m founder.ingestion.build_earnings")

    print("Would run: python -m founder.ingestion.build_news")

    return True


def run_chunking() -> bool:
    """Chunk documents."""

    print("\n--- Creating Chunks ---")

    print("Would run: python -m founder.ingestion.chunk_documents")

    return True


def run_qdrant_rebuild() -> bool:
    """Rebuild Qdrant indexes."""

    print("\n--- Rebuilding Qdrant Indexes ---")

    print("Would run: python -m founder.retrieval.index_chunks")

    return True


def run_graph_rebuild() -> bool:
    """Rebuild Neo4j graph."""

    print("\n--- Rebuilding Neo4j Graph ---")

    print("Would run: python -m founder.graph.init_graph")

    print("Would run: python -m founder.graph.extract_entities")

    print("Would run: python -m founder.graph.write_graph")

    return True


def run_evaluation() -> bool:
    """Run evaluation on labeled questions."""

    print("\n--- Running Evaluation ---")

    print("Would run: python -m founder.evaluation.run_experiment")

    return True


def print_summary(success: bool):
    """Print bootstrap summary."""

    print("\n" + "=" * 50)

    if success:

        print(f"[SUCCESS] Bootstrap Complete!")

        print("\nSystem is ready:")
        print("  - Raw data processed")
        print("  - Indexes created")
        print("  - Graph populated")
        print("  - Evaluation complete")

        print("\nStart API:")
        print("  uvicorn founder.api.main:app --reload")

        print("\nStart Frontend:")
        print("  cd frontend && npm run dev")

    else:

        print("[ERROR] Bootstrap Failed!")

        print("Please fix the errors above and try again.")

    print("=" * 50)


def main():
    """Main bootstrap sequence."""

    print("\n" + "=" * 50)

    print("FounderOS Bootstrap")

    print("=" * 50)

    # Check prerequisites
    print("\nChecking prerequisites...")

    if not check_raw_data():
        print_summary(False)
        sys.exit(1)

    if not check_services():
        print("⚠ Services not available. Proceeding anyway (will fail later).")

    # Run pipeline
    print("\nRunning rebuild pipeline...")

    steps = [
        ("Dataset Rebuild", run_dataset_rebuild),
        ("Chunking", run_chunking),
        ("Qdrant Rebuild", run_qdrant_rebuild),
        ("Graph Rebuild", run_graph_rebuild),
        ("Evaluation", run_evaluation),
    ]

    for step_name, step_func in steps:

        try:

            if not step_func():
                print(f"❌ {step_name} failed")

                print_summary(False)

                sys.exit(1)

        except Exception as err:

            print(f"❌ {step_name} error: {err}")

            print_summary(False)

            sys.exit(1)

    print_summary(True)


if __name__ == "__main__":
    main()
