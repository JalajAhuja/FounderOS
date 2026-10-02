"""Deterministic query broadening for corrective retrieval (Step 17).

Not a paraphrasing/LLM rewrite -- strips specific period qualifiers so a
retry round is not still narrowed to a single reporting period.
"""

import re


_PERIOD_PATTERN = re.compile(
    r"\b(Q[1-4]\s?\d{4}|FY\s?\d{4}|\d{4})\b",
    re.IGNORECASE,
)


def broaden_query(query: str) -> str:

    stripped = _PERIOD_PATTERN.sub("", query)

    stripped = re.sub(r"\s{2,}", " ", stripped).strip()

    return stripped or query
