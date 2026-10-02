from founder.retrieval.evidence import Evidence
from founder.retrieval.reranker import Reranker


def _evidence(evidence_id, text):

    return Evidence(evidence_id=evidence_id, source="Qdrant", text=text)


def test_rerank_disabled_returns_original_order_truncated():

    reranker = Reranker(enabled=False)

    documents = [_evidence("e1", "a"), _evidence("e2", "b"), _evidence("e3", "c")]

    result = reranker.rerank("query", documents, top_k=2)

    assert [item.evidence_id for item in result] == ["e1", "e2"]


def test_rerank_reorders_by_model_score(monkeypatch):

    reranker = Reranker(enabled=True)

    documents = [_evidence("e1", "low"), _evidence("e2", "high")]

    class FakeModel:

        def rerank(self, query, texts, **kwargs):
            # Reverse order: second document scores higher.
            return [0.1, 0.9]

    monkeypatch.setattr(reranker, "_get_model", lambda: FakeModel())

    result = reranker.rerank("query", documents, top_k=2)

    assert [item.evidence_id for item in result] == ["e2", "e1"]
    assert result[0].metadata["rerank_score"] == 0.9


def test_rerank_falls_back_to_original_order_on_model_failure(monkeypatch):

    reranker = Reranker(enabled=True)

    documents = [_evidence("e1", "a"), _evidence("e2", "b")]

    def _raise():
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(reranker, "_get_model", _raise)

    result = reranker.rerank("query", documents, top_k=2)

    assert [item.evidence_id for item in result] == ["e1", "e2"]


def test_rerank_no_documents_returns_empty():

    reranker = Reranker(enabled=True)

    assert reranker.rerank("query", [], top_k=5) == []
