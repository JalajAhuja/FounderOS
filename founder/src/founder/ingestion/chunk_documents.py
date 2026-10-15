import json
import re
from pathlib import Path
from typing import Any

import tiktoken

# ============================================================
# PATHS
# ============================================================

PRIMARY_DIR = Path("data/03_primary")
OUTPUT_DIR = Path("data/04_chunks")

DOCUMENTS_FILE = PRIMARY_DIR / "documents.jsonl"
EARNINGS_FILE = PRIMARY_DIR / "earnings.jsonl"
NEWS_FILE = PRIMARY_DIR / "news.jsonl"

SEC_OUTPUT = OUTPUT_DIR / "sec_chunks.jsonl"
EARNINGS_OUTPUT = OUTPUT_DIR / "earnings_chunks.jsonl"
NEWS_OUTPUT = OUTPUT_DIR / "news_chunks.jsonl"
ALL_OUTPUT = OUTPUT_DIR / "chunks.jsonl"


# ============================================================
# CHUNKING CONFIGURATION
# ============================================================

SEC_MAX_TOKENS = 850
SEC_OVERLAP_TOKENS = 100

EARNINGS_MAX_TOKENS = 700
EARNINGS_OVERLAP_TOKENS = 80

NEWS_MAX_TOKENS = 500
NEWS_OVERLAP_TOKENS = 50

MIN_CHUNK_TOKENS = 40


# ============================================================
# TOKENIZER
# ============================================================

ENCODER = tiktoken.get_encoding("cl100k_base")


# ============================================================
# GENERAL HELPERS
# ============================================================

def read_jsonl(path: Path):
    if not path.exists():
        print(f"WARNING: file does not exist: {path}")
        return []

    records = []

    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(
                    f"WARNING: invalid JSON in {path} "
                    f"line {line_number}: {e}"
                )

    return records


def write_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )


def token_count(text: str) -> int:
    return len(ENCODER.encode(text))


def normalize_text(text: Any) -> str:
    if text is None:
        return ""

    text = str(text)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive whitespace while preserving paragraphs.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def get_first(record, *keys, default=None):
    for key in keys:
        value = record.get(key)

        if value is not None and value != "":
            return value

    return default


# ============================================================
# STRUCTURAL SEC SECTION DETECTION
# ============================================================

SEC_SECTION_PATTERNS = [
    (
        re.compile(
            r"(?im)^\s*(item\s+1a\.?\s+"
            r"risk\s+factors)\s*$"
        ),
        "Item 1A - Risk Factors",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+1\.?\s+"
            r"business)\s*$"
        ),
        "Item 1 - Business",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+2\.?\s+"
            r"properties)\s*$"
        ),
        "Item 2 - Properties",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+3\.?\s+"
            r"legal\s+proceedings)\s*$"
        ),
        "Item 3 - Legal Proceedings",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+5\.?\s+"
            r"market\s+for)\s*$"
        ),
        "Item 5 - Market for Registrant's Common Equity",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+7\.?\s+"
            r"management[’']?s\s+discussion)"
        ),
        "Item 7 - Management's Discussion and Analysis",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+7a\.?\s+"
            r"quantitative)"
        ),
        "Item 7A - Quantitative and Qualitative Disclosures",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+8\.?\s+"
            r"financial\s+statements)"
        ),
        "Item 8 - Financial Statements",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+9a\.?\s+"
            r"controls)"
        ),
        "Item 9A - Controls and Procedures",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+10\.?\s+"
            r"directors)"
        ),
        "Item 10 - Directors and Officers",
    ),
    (
        re.compile(
            r"(?im)^\s*(item\s+11\.?\s+"
            r"executive\s+compensation)"
        ),
        "Item 11 - Executive Compensation",
    ),
]


def detect_sec_sections(text: str):
    """
    Attempts to identify major SEC Item sections.

    If no recognizable sections are found,
    the entire document becomes one structural section.
    """

    matches = []

    for pattern, section_name in SEC_SECTION_PATTERNS:
        for match in pattern.finditer(text):
            matches.append(
                (
                    match.start(),
                    match.end(),
                    section_name,
                )
            )

    matches.sort(key=lambda x: x[0])

    if not matches:
        return [
            (
                "Document",
                text,
            )
        ]

    sections = []

    # Text before first detected section.
    first_start = matches[0][0]

    if first_start > 0:
        prefix = text[:first_start].strip()

        if prefix:
            sections.append(
                (
                    "Document Introduction",
                    prefix,
                )
            )

    for i, match in enumerate(matches):

        start = match[1]

        if i + 1 < len(matches):
            end = matches[i + 1][0]
        else:
            end = len(text)

        body = text[start:end].strip()

        if body:
            sections.append(
                (
                    match[2],
                    body,
                )
            )

    return sections


# ============================================================
# PARAGRAPH SPLITTING
# ============================================================

def split_paragraphs(text: str):
    """
    Split text while preserving meaningful paragraph boundaries.
    """

    text = normalize_text(text)

    if not text:
        return []

    paragraphs = re.split(
        r"\n\s*\n",
        text
    )

    result = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        result.append(paragraph)

    return result


# ============================================================
# TOKEN-AWARE PACKING
# ============================================================

def pack_paragraphs(
    paragraphs,
    max_tokens,
    overlap_tokens,
):
    """
    Packs paragraphs into chunks under max_tokens.

    Overlap is paragraph-based rather than blindly slicing
    arbitrary characters.
    """

    chunks = []

    current = []
    current_tokens = 0

    for paragraph in paragraphs:

        paragraph_tokens = token_count(paragraph)

        # Extremely large paragraph.
        if paragraph_tokens > max_tokens:

            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_tokens = 0

            token_ids = ENCODER.encode(paragraph)

            start = 0

            while start < len(token_ids):

                end = min(
                    start + max_tokens,
                    len(token_ids)
                )

                piece = ENCODER.decode(
                    token_ids[start:end]
                ).strip()

                if piece:
                    chunks.append(piece)

                start = end

            continue

        # Normal paragraph.
        if (
            current
            and current_tokens + paragraph_tokens > max_tokens
        ):

            chunks.append(
                "\n\n".join(current)
            )

            # Build overlap from the end of the previous chunk.
            overlap = []
            overlap_count = 0

            for previous in reversed(current):

                previous_tokens = token_count(previous)

                if (
                    overlap_count + previous_tokens
                    > overlap_tokens
                ):
                    break

                overlap.insert(0, previous)
                overlap_count += previous_tokens

            current = overlap
            current_tokens = overlap_count

        current.append(paragraph)
        current_tokens += paragraph_tokens

    if current:
        chunks.append(
            "\n\n".join(current)
        )

    return chunks


# ============================================================
# SEC CHUNKING
# ============================================================

def chunk_sec_document(record):

    document_id = get_first(
        record,
        "document_id",
        "id",
        default="unknown_document",
    )

    ticker = get_first(
        record,
        "ticker",
        default="",
    )

    text = normalize_text(
        get_first(
            record,
            "text",
            "content",
            default="",
        )
    )

    if not text:
        return []

    document_type = get_first(
        record,
        "document_type",
        "form",
        default="SEC filing",
    )

    published_at = get_first(
        record,
        "published_at",
        "filing_date",
        "filed",
    )

    metadata = record.get("metadata", {})

    sections = detect_sec_sections(text)

    output = []

    global_index = 0

    for section_name, section_text in sections:

        paragraphs = split_paragraphs(section_text)

        chunks = pack_paragraphs(
            paragraphs,
            SEC_MAX_TOKENS,
            SEC_OVERLAP_TOKENS,
        )

        for local_index, chunk_text in enumerate(chunks):

            tokens = token_count(chunk_text)

            if tokens < MIN_CHUNK_TOKENS:
                continue

            chunk_id = (
                f"{document_id}"
                f"__"
                f"{section_name.replace(' ', '_')}"
                f"__"
                f"{global_index:04d}"
            )

            output.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "text": chunk_text,
                    "source": "SEC",
                    "ticker": ticker,
                    "document_type": document_type,
                    "section": section_name,
                    "speaker": None,
                    "year": get_first(
                        record,
                        "year",
                        default=None,
                    ),
                    "quarter": get_first(
                        record,
                        "quarter",
                        default=None,
                    ),
                    "published_at": published_at,
                    "chunk_index": global_index,
                    "section_chunk_index": local_index,
                    "token_count": tokens,
                    "metadata": metadata,
                }
            )

            global_index += 1

    return output


# ============================================================
# EARNINGS CALL CHUNKING
# ============================================================

def extract_structured_segments(structured_content):
    """
    Attempts to extract speaker/content pairs from the
    structured_content field.

    Handles several possible dataset representations.
    """

    segments = []

    if not structured_content:
        return segments

    # --------------------------------------------------------
    # Case 1: list of dictionaries
    # --------------------------------------------------------

    if isinstance(structured_content, list):

        for item in structured_content:

            if not isinstance(item, dict):
                continue

            speaker = get_first(
                item,
                "speaker",
                "name",
                "speaker_name",
                default=None,
            )

            content = get_first(
                item,
                "content",
                "text",
                "utterance",
                default=None,
            )

            if content:
                segments.append(
                    {
                        "speaker": speaker,
                        "text": normalize_text(content),
                    }
                )

    # --------------------------------------------------------
    # Case 2: dictionary containing turns
    # --------------------------------------------------------

    elif isinstance(structured_content, dict):

        for key in (
            "segments",
            "turns",
            "content",
            "dialogue",
            "speakers",
        ):

            value = structured_content.get(key)

            if isinstance(value, list):

                for item in value:

                    if not isinstance(item, dict):
                        continue

                    speaker = get_first(
                        item,
                        "speaker",
                        "name",
                        "speaker_name",
                        default=None,
                    )

                    content = get_first(
                        item,
                        "content",
                        "text",
                        "utterance",
                        default=None,
                    )

                    if content:
                        segments.append(
                            {
                                "speaker": speaker,
                                "text": normalize_text(content),
                            }
                        )

    return segments


def chunk_earnings_document(record):

    document_id = get_first(
        record,
        "document_id",
        "id",
        default="unknown_earnings",
    )

    ticker = get_first(
        record,
        "ticker",
        "symbol",
        default="",
    )

    year = get_first(
        record,
        "year",
    )

    quarter = get_first(
        record,
        "quarter",
    )

    published_at = get_first(
        record,
        "published_at",
        "date",
    )

    structured_content = record.get(
        "structured_content"
    )

    segments = extract_structured_segments(
        structured_content
    )

    output = []

    # ========================================================
    # Structured speaker path
    # ========================================================

    if segments:

        current_segments = []
        current_tokens = 0

        global_index = 0

        for segment in segments:

            speaker = segment.get(
                "speaker"
            )

            segment_text = segment.get(
                "text",
                ""
            )

            if not segment_text:
                continue

            formatted = (
                f"{speaker}: {segment_text}"
                if speaker
                else segment_text
            )

            segment_tokens = token_count(
                formatted
            )

            if (
                current_segments
                and current_tokens + segment_tokens
                > EARNINGS_MAX_TOKENS
            ):

                chunk_text = "\n\n".join(
                    current_segments
                )

                if token_count(chunk_text) >= MIN_CHUNK_TOKENS:

                    speakers = []

                    for item in current_segments:
                        match = re.match(
                            r"^([^:]{1,100}): ",
                            item
                        )

                        if match:
                            speakers.append(
                                match.group(1)
                            )

                    speaker_value = (
                        speakers[0]
                        if len(set(speakers)) == 1
                        else None
                    )

                    output.append(
                        {
                            "chunk_id": (
                                f"{document_id}"
                                f"__"
                                f"{global_index:04d}"
                            ),
                            "document_id": document_id,
                            "text": chunk_text,
                            "source": "earnings_call",
                            "ticker": ticker,
                            "document_type": "earnings_call",
                            "section": "earnings_call",
                            "speaker": speaker_value,
                            "year": year,
                            "quarter": quarter,
                            "published_at": published_at,
                            "chunk_index": global_index,
                            "token_count": token_count(
                                chunk_text
                            ),
                            "metadata": {
                                "company": record.get(
                                    "company"
                                ),
                            },
                        }
                    )

                    global_index += 1

                # Simple segment overlap.
                overlap_segments = []

                overlap_tokens = 0

                for previous in reversed(
                    current_segments
                ):

                    t = token_count(
                        previous
                    )

                    if (
                        overlap_tokens + t
                        > EARNINGS_OVERLAP_TOKENS
                    ):
                        break

                    overlap_segments.insert(
                        0,
                        previous,
                    )

                    overlap_tokens += t

                current_segments = (
                    overlap_segments
                )

                current_tokens = (
                    overlap_tokens
                )

            current_segments.append(
                formatted
            )

            current_tokens += segment_tokens

        # Final chunk.

        if current_segments:

            chunk_text = "\n\n".join(
                current_segments
            )

            if token_count(chunk_text) >= MIN_CHUNK_TOKENS:

                output.append(
                    {
                        "chunk_id": (
                            f"{document_id}"
                            f"__"
                            f"{global_index:04d}"
                        ),
                        "document_id": document_id,
                        "text": chunk_text,
                        "source": "earnings_call",
                        "ticker": ticker,
                        "document_type": "earnings_call",
                        "section": "earnings_call",
                        "speaker": None,
                        "year": year,
                        "quarter": quarter,
                        "published_at": published_at,
                        "chunk_index": global_index,
                        "token_count": token_count(
                            chunk_text
                        ),
                        "metadata": {
                            "company": record.get(
                                "company"
                            ),
                        },
                    }
                )

        return output

    # ========================================================
    # Fallback: raw transcript
    # ========================================================

    text = normalize_text(
        get_first(
            record,
            "text",
            "content",
            default="",
        )
    )

    if not text:
        return []

    paragraphs = split_paragraphs(text)

    chunks = pack_paragraphs(
        paragraphs,
        EARNINGS_MAX_TOKENS,
        EARNINGS_OVERLAP_TOKENS,
    )

    for index, chunk_text in enumerate(chunks):

        if token_count(chunk_text) < MIN_CHUNK_TOKENS:
            continue

        output.append(
            {
                "chunk_id": (
                    f"{document_id}"
                    f"__"
                    f"{index:04d}"
                ),
                "document_id": document_id,
                "text": chunk_text,
                "source": "earnings_call",
                "ticker": ticker,
                "document_type": "earnings_call",
                "section": "earnings_call",
                "speaker": None,
                "year": year,
                "quarter": quarter,
                "published_at": published_at,
                "chunk_index": index,
                "token_count": token_count(
                    chunk_text
                ),
                "metadata": {
                    "company": record.get(
                        "company"
                    ),
                },
            }
        )

    return output


# ============================================================
# NEWS CHUNKING
# ============================================================

def chunk_news_document(record):

    document_id = get_first(
        record,
        "document_id",
        "id",
        default="unknown_news",
    )

    ticker = get_first(
        record,
        "ticker",
        default="",
    )

    title = get_first(
        record,
        "title",
        "headline",
        default="",
    )

    text = normalize_text(
        get_first(
            record,
            "text",
            "content",
            "description",
            "snippet",
            default="",
        )
    )

    if not text and title:
        text = title

    if not text:
        return []

    published_at = get_first(
        record,
        "published_at",
        "date",
        "datetime",
    )

    url = get_first(
        record,
        "url",
        "link",
        "source_url",
    )

    domain = get_first(
        record,
        "domain",
        "source",
    )

    # News articles are generally shorter and should retain
    # title + body together.

    full_text = (
        f"Title: {title}\n\n{text}"
        if title
        else text
    )

    paragraphs = split_paragraphs(
        full_text
    )

    chunks = pack_paragraphs(
        paragraphs,
        NEWS_MAX_TOKENS,
        NEWS_OVERLAP_TOKENS,
    )

    output = []

    for index, chunk_text in enumerate(chunks):

        if token_count(chunk_text) < MIN_CHUNK_TOKENS:
            continue

        output.append(
            {
                "chunk_id": (
                    f"{document_id}"
                    f"__"
                    f"{index:04d}"
                ),
                "document_id": document_id,
                "text": chunk_text,
                "source": "news",
                "ticker": ticker,
                "document_type": "news",
                "section": "article",
                "speaker": None,
                "year": get_first(
                    record,
                    "year",
                    default=None,
                ),
                "quarter": None,
                "published_at": published_at,
                "chunk_index": index,
                "token_count": token_count(
                    chunk_text
                ),
                "metadata": {
                    "title": title,
                    "url": url,
                    "domain": domain,
                },
            }
        )

    return output


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("FounderOS - Source-Aware Chunking")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # SEC
    # --------------------------------------------------------

    print("\n[1/3] Chunking SEC documents...")

    sec_records = read_jsonl(
        DOCUMENTS_FILE
    )

    sec_chunks = []

    for index, record in enumerate(
        sec_records,
        start=1,
    ):

        chunks = chunk_sec_document(
            record
        )

        sec_chunks.extend(chunks)

        if index % 100 == 0:
            print(
                f"  Processed {index} SEC documents..."
            )

    write_jsonl(
        SEC_OUTPUT,
        sec_chunks,
    )

    print(
        f"  SEC documents: {len(sec_records):,}"
    )

    print(
        f"  SEC chunks:    {len(sec_chunks):,}"
    )

    # --------------------------------------------------------
    # EARNINGS
    # --------------------------------------------------------

    print("\n[2/3] Chunking earnings calls...")

    earnings_records = read_jsonl(
        EARNINGS_FILE
    )

    earnings_chunks = []

    for index, record in enumerate(
        earnings_records,
        start=1,
    ):

        chunks = chunk_earnings_document(
            record
        )

        earnings_chunks.extend(chunks)

        if index % 100 == 0:
            print(
                f"  Processed {index} earnings calls..."
            )

    write_jsonl(
        EARNINGS_OUTPUT,
        earnings_chunks,
    )

    print(
        f"  Earnings documents: {len(earnings_records):,}"
    )

    print(
        f"  Earnings chunks:    {len(earnings_chunks):,}"
    )

    # --------------------------------------------------------
    # NEWS
    # --------------------------------------------------------

    print("\n[3/3] Chunking news...")

    news_records = read_jsonl(
        NEWS_FILE
    )

    news_chunks = []

    for index, record in enumerate(
        news_records,
        start=1,
    ):

        chunks = chunk_news_document(
            record
        )

        news_chunks.extend(chunks)

        if index % 100 == 0:
            print(
                f"  Processed {index} news documents..."
            )

    write_jsonl(
        NEWS_OUTPUT,
        news_chunks,
    )

    print(
        f"  News documents: {len(news_records):,}"
    )

    print(
        f"  News chunks:    {len(news_chunks):,}"
    )

    # --------------------------------------------------------
    # COMBINED
    # --------------------------------------------------------

    all_chunks = (
        sec_chunks
        + earnings_chunks
        + news_chunks
    )

    write_jsonl(
        ALL_OUTPUT,
        all_chunks,
    )

    print("\n" + "=" * 70)
    print("CHUNKING COMPLETE")
    print("=" * 70)

    print(
        f"SEC chunks:       {len(sec_chunks):,}"
    )

    print(
        f"Earnings chunks:  {len(earnings_chunks):,}"
    )

    print(
        f"News chunks:      {len(news_chunks):,}"
    )

    print(
        f"TOTAL chunks:     {len(all_chunks):,}"
    )

    print(
        f"\nOutput directory:"
        f" {OUTPUT_DIR}"
    )

    print(
        f"Combined file:"
        f" {ALL_OUTPUT}"
    )


if __name__ == "__main__":
    main()
