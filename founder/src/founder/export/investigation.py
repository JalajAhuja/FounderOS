"""Build and write portable investigation packs."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from founder.export.models import InvestigationPack


def build_investigation_pack(query: str, result: dict[str, Any] | None = None) -> InvestigationPack:
    result = result or {}
    answer = result.get("answer") or result.get("text") or "No answer was generated."
    if isinstance(answer, dict):
        answer = answer.get("text") or answer.get("answer") or "No answer was generated."
    evidence = result.get("evidence", [])
    return InvestigationPack(
        question=query, answer=str(answer), claims=result.get("claims", []),
        timeline=result.get("timeline", []), graph_findings=result.get("graph_findings", []),
        financial_facts=result.get("financial_facts", []), sources=evidence or result.get("sources", []),
        limitations=result.get("limitations", ["This export contains only evidence returned by the configured services."]),
        trace_id=result.get("trace_id"),
    )


def write_investigation(pack: InvestigationPack, output_dir: str | Path = "artifacts") -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"investigation_{stamp}.md"
    lines = [f"# Investigation: {pack.question}", "", "## Answer", pack.answer, ""]
    if pack.claims:
        lines += ["## Claims"] + [f"- {claim.get('text', claim)}" for claim in pack.claims] + [""]
    if pack.sources:
        lines += ["## Sources"] + [f"- `{source.get('evidence_id', 'unknown')}` {source.get('source', '')}: {source.get('text', '')}" for source in pack.sources] + [""]
    if pack.timeline:
        lines += ["## Timeline"] + [f"- {item}" for item in pack.timeline] + [""]
    if pack.limitations:
        lines += ["## Limitations"] + [f"- {item}" for item in pack.limitations] + [""]
    if pack.trace_id:
        lines += [f"Trace ID: `{pack.trace_id}`", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def investigation_json(pack: InvestigationPack) -> str:
    return json.dumps(asdict(pack), indent=2, default=str)
