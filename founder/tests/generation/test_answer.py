import json

from founder.generation import answer as answer_module
from founder.retrieval.evidence import Evidence


class FakeMessage:

    def __init__(self, content):
        self.content = content


class FakeChoice:

    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:

    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeCompletions:

    def __init__(self, content):
        self._content = content

    def create(self, **kwargs):
        return FakeResponse(self._content)


class FakeChat:

    def __init__(self, content):
        self.completions = FakeCompletions(content)


class FakeOpenAI:

    def __init__(self, content):
        self.chat = FakeChat(content)


def _evidence(evidence_id="e1"):

    return Evidence(
        evidence_id=evidence_id,
        source="Qdrant",
        text="Microsoft discussed AI monetization.",
        ticker="MSFT",
        published_at="2025-06-01",
    )


def test_generate_answer_without_evidence_returns_fallback():

    result = answer_module.generate_answer("q", [])

    assert "don't have enough evidence" in result.answer
    assert result.citations == []
    assert result.claims == []


def test_generate_answer_drops_hallucinated_evidence_ids(monkeypatch):

    payload = json.dumps(
        {
            "answer": "Microsoft discussed AI monetization.",
            "claims": [
                {
                    "text": "Microsoft discussed AI monetization.",
                    "evidence_ids": ["e1", "not-a-real-id"],
                    "claim_type": "source_claim",
                    "confidence": 0.9,
                }
            ],
            "limitations": [],
        }
    )

    monkeypatch.setattr(
        answer_module,
        "OpenAI",
        lambda api_key=None: FakeOpenAI(payload),
    )

    result = answer_module.generate_answer(
        "What did Microsoft say?", [_evidence("e1")]
    )

    assert len(result.claims) == 1
    assert result.claims[0].evidence_ids == ["e1"]
    assert len(result.citations) == 1
    assert result.citations[0].evidence_id == "e1"


def test_generate_answer_drops_claim_with_only_hallucinated_ids(monkeypatch):

    payload = json.dumps(
        {
            "answer": "...",
            "claims": [
                {
                    "text": "Invented claim.",
                    "evidence_ids": ["not-a-real-id"],
                    "claim_type": "inference",
                    "confidence": 0.5,
                }
            ],
            "limitations": [],
        }
    )

    monkeypatch.setattr(
        answer_module,
        "OpenAI",
        lambda api_key=None: FakeOpenAI(payload),
    )

    result = answer_module.generate_answer("q", [_evidence("e1")])

    assert result.claims == []
    assert result.citations == []


def test_generate_answer_appends_insufficiency_limitation(monkeypatch):

    payload = json.dumps(
        {"answer": "Partial answer.", "claims": [], "limitations": []}
    )

    monkeypatch.setattr(
        answer_module,
        "OpenAI",
        lambda api_key=None: FakeOpenAI(payload),
    )

    result = answer_module.generate_answer(
        "q",
        [_evidence("e1")],
        sufficiency={"sufficient": False, "reason": ["Only one period found."]},
    )

    assert any(
        "Only one period found." in limitation
        for limitation in result.limitations
    )
