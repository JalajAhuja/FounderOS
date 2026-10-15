from pathlib import Path

from bs4 import BeautifulSoup

# ============================================================
# CONFIG
# ============================================================

DOCUMENTS_DIR = Path(
    "data/01_raw/sec/documents"
)

CLEAN_DIR = Path(
    "data/01_raw/sec/clean"
)


# ============================================================
# HTML -> CLEAN TEXT
# ============================================================

def html_to_text(html):

    # IMPORTANT:
    # Use Python's built-in HTML parser.
    # This avoids requiring lxml.

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Remove elements that don't contain useful
    # document text.

    for tag in soup.find_all(
        [
            "script",
            "style",
            "noscript",
            "svg"
        ]
    ):
        tag.decompose()

    # Extract text
    text = soup.get_text(
        separator="\n"
    )

    # Clean whitespace
    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        lines.append(line)

    return "\n".join(lines)


# ============================================================
# PROCESS ONE HTML FILE
# ============================================================

def process_file(html_file):

    # Ignore metadata files
    if html_file.name.endswith(
        ".metadata.json"
    ):
        return False

    # Preserve original directory structure
    #
    # documents/
    #   DDOG/
    #      10-K/
    #         2026/
    #            filing.htm
    #
    # becomes
    #
    # clean/
    #   DDOG/
    #      10-K/
    #         2026/
    #            filing.txt

    relative = (
        html_file.relative_to(
            DOCUMENTS_DIR
        )
    )

    output_file = (
        CLEAN_DIR
        / relative.parent
        / (
            html_file.stem
            + ".txt"
        )
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        f"Cleaning: {html_file}"
    )

    try:

        html = html_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        text = html_to_text(
            html
        )

        # Make sure we didn't accidentally
        # create an empty document.

        if not text.strip():

            print(
                f"WARNING: Empty text: "
                f"{html_file}"
            )

            return False

        output_file.write_text(
            text,
            encoding="utf-8"
        )

        return True

    except Exception as e:

        print(
            f"ERROR: {html_file}"
        )

        print(e)

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FounderOS - SEC HTML Cleaner")
    print("=" * 60)

    if not DOCUMENTS_DIR.exists():

        print(
            "ERROR: Documents directory "
            "does not exist:"
        )

        print(
            DOCUMENTS_DIR
        )

        return

    CLEAN_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    html_files = list(
        DOCUMENTS_DIR.rglob(
            "*.htm"
        )
    )

    print(
        f"HTML files found: "
        f"{len(html_files)}"
    )

    successful = 0
    failed = 0

    for html_file in html_files:

        success = process_file(
            html_file
        )

        if success:
            successful += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print("Cleaning complete")
    print("=" * 60)

    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed:     {failed}"
    )

    print(
        f"Output:     {CLEAN_DIR}"
    )

    print("=" * 60)


if __name__ == "__main__":

    main()
