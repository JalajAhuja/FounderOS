from founder.export.investigation import (
    build_investigation_pack,
    investigation_json,
    write_investigation,
)


def test_investigation_pack_contains_claims_and_sources(tmp_path):
    pack = build_investigation_pack("What changed?", {"answer": "A change.", "claims": [{"text": "A change."}], "evidence": [{"evidence_id": "e1", "source": "SEC", "text": "Source"}]})
    output = write_investigation(pack, tmp_path)
    assert output.exists()
    assert "What changed?" in output.read_text(encoding="utf-8")
    assert '"evidence_id": "e1"' in investigation_json(pack)
