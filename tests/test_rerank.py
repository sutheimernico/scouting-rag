"""Unit tests for rerank logic with an injected scorer (no model load)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rerank import RerankedRetriever, rerank


def _cands(*ids):
    return [{"chunk_id": i, "doc_id": f"d/{i}", "text": f"text {i}", "score": 0.0} for i in ids]


def test_rerank_orders_by_scorer_and_cuts_k():
    out = rerank("q", _cands("a", "b", "c"), k=2, scorer=lambda pairs: [0.1, 0.9, 0.5])
    assert [c["chunk_id"] for c in out] == ["b", "c"]
    assert out[0]["score"] == 0.9


def test_rerank_empty_candidates():
    assert rerank("q", [], k=5, scorer=lambda pairs: []) == []


def test_reranked_retriever_pulls_top_n_then_cuts_k():
    class FakeBase:
        def __init__(self):
            self.requested_k = None

        def search(self, query, k):
            self.requested_k = k
            return _cands(*[f"c{i}" for i in range(k)])

    base = FakeBase()
    retriever = RerankedRetriever(base, top_n=7, scorer=lambda pairs: list(range(len(pairs))))
    out = retriever.search("q", k=3)
    assert base.requested_k == 7
    assert len(out) == 3
    assert out[0]["chunk_id"] == "c6"  # highest synthetic score = last candidate
