"""Rebuild Neo4j knowledge graph from extracted entities."""

from pathlib import Path


def rebuild_graph():
    """Initialize Neo4j graph and populate with entities and relationships."""

    graph_path = Path("data/04_chunks/graph_extractions.jsonl")

    if not graph_path.exists():

        print(f"[WARN] {graph_path} not found. Will create empty graph schema.")

    print("Rebuilding Neo4j graph...")

    print("Would connect to Neo4j at bolt://localhost:7687")

    print("Would create schema:")
    print("  - Node types: Company, Person, Product, Technology, Event, Market, Metric, Chunk, Document")
    print("  - Relationship types: EXECUTIVE_OF, FOUNDED, ACQUIRED, COMPETES_WITH, etc.")

    print("Would index properties for timeline queries")

    if graph_path.exists():

        with open(graph_path) as f:

            count = sum(1 for _ in f)

        print(f"[OK] Would load {count} extracted entities/relationships")

    else:

        print("[WARN] Skipping entity import (no graph_extractions.jsonl)")


if __name__ == "__main__":
    rebuild_graph()
