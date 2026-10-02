import json
from pathlib import Path

from openai import OpenAI

from founder.graph.config import (
    CHUNKS_FILE,
    EXTRACTIONS_FILE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MAX_CHUNKS,
)
from founder.graph.schema import (
    SYSTEM_PROMPT,
)


client = OpenAI(
    api_key=OPENAI_API_KEY
)


# ============================================================
# JSON SCHEMA
# ============================================================

EXTRACTION_SCHEMA = {
    "type": "object",

    "properties": {

        "entities": {
            "type": "array",

            "items": {

                "type": "object",

                "properties": {

                    "name": {
                        "type": "string"
                    },

                    "type": {
                        "type": "string",
                        "enum": [
                            "Company",
                            "Person",
                            "Product",
                            "Technology",
                            "Event",
                            "Market",
                            "Metric",
                        ],
                    },
                },

                "required": [
                    "name",
                    "type",
                ],

                "additionalProperties": False,
            },
        },

        "relationships": {

            "type": "array",

            "items": {

                "type": "object",

                "properties": {

                    "source": {
                        "type": "string"
                    },

                    "source_type": {
                        "type": "string"
                    },

                    "relationship": {
                        "type": "string"
                    },

                    "target": {
                        "type": "string"
                    },

                    "target_type": {
                        "type": "string"
                    },

                    "evidence": {
                        "type": "string"
                    },

                    "confidence": {
                        "type": "number"
                    },
                },

                "required": [
                    "source",
                    "source_type",
                    "relationship",
                    "target",
                    "target_type",
                    "evidence",
                    "confidence",
                ],

                "additionalProperties": False,
            },
        },
    },

    "required": [
        "entities",
        "relationships",
    ],

    "additionalProperties": False,
}


def extract_chunk(chunk):

    chunk_id = chunk[
        "chunk_id"
    ]

    text = chunk.get(
        "text",
        "",
    )

    prompt = f"""
SOURCE CHUNK ID:
{chunk_id}

SOURCE:
{chunk.get("source")}

TICKER:
{chunk.get("ticker")}

DOCUMENT TYPE:
{chunk.get("document_type")}

SECTION:
{chunk.get("section")}

DATE:
{chunk.get("published_at")}

TEXT:
{text}
"""

    response = client.chat.completions.create(

        model=OPENAI_MODEL,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },

            {
                "role": "user",
                "content": prompt,
            },
        ],

        response_format={
            "type": "json_schema",

            "json_schema": {
                "name": "founderos_graph_extraction",
                "strict": True,
                "schema": EXTRACTION_SCHEMA,
            },
        },

    )

    content = response.choices[
        0
    ].message.content

    result = json.loads(
        content
    )

    return {
        "chunk_id": chunk_id,
        "document_id": chunk.get(
            "document_id"
        ),
        "source": chunk.get(
            "source"
        ),
        "ticker": chunk.get(
            "ticker"
        ),
        "published_at": chunk.get(
            "published_at"
        ),
        "entities": result.get(
            "entities",
            [],
        ),
        "relationships": result.get(
            "relationships",
            [],
        ),
    }


def load_chunks():

    chunks = []

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            chunks.append(
                json.loads(line)
            )

            if (
                MAX_CHUNKS is not None
                and len(chunks) >= MAX_CHUNKS
            ):
                break

    return chunks


def main():

    if not OPENAI_API_KEY:

        raise RuntimeError(
            "OPENAI_API_KEY is missing."
        )

    print(
        "\nFounderOS - Graph Extraction"
    )

    chunks = load_chunks()

    print(
        f"Chunks to process: "
        f"{len(chunks)}"
    )

    EXTRACTIONS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        EXTRACTIONS_FILE,
        "w",
        encoding="utf-8",
    ) as output:

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            print(
                f"[{index}/{len(chunks)}] "
                f"{chunk['chunk_id']}"
            )

            try:

                extraction = extract_chunk(
                    chunk
                )

                output.write(
                    json.dumps(
                        extraction,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

                output.flush()

                print(
                    f"  entities: "
                    f"{len(extraction['entities'])}"
                )

                print(
                    f"  relationships: "
                    f"{len(extraction['relationships'])}"
                )

            except Exception as e:

                print(
                    f"  ERROR: {e}"
                )

    print(
        "\nGraph extraction complete."
    )

    print(
        f"Output: {EXTRACTIONS_FILE}"
    )


if __name__ == "__main__":
    main()