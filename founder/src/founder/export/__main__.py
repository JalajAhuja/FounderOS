"""Command line export entry point."""

import argparse

from founder.export.investigation import build_investigation_pack, write_investigation


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m founder.export")
    subparsers = parser.add_subparsers(dest="command", required=True)
    investigation = subparsers.add_parser("investigation")
    investigation.add_argument("--query", required=True)
    investigation.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()
    if args.command == "investigation":
        print(write_investigation(build_investigation_pack(args.query), args.output_dir))


if __name__ == "__main__":
    main()
