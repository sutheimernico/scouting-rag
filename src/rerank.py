"""Cycle 3: cross-encoder reranking over retriever candidates.

bge-reranker-v2-m3 (multilingual, same family as the embedder) scores
(query, chunk) pairs jointly; the base retriever supplies TOP_N
candidates, the reranker reorders, top-k go to the generator.

The explicit trade-off of this cycle is latency: a cross-encoder
forward pass per candidate on CPU. TOP_N=30 is the cycle-default
(documented decision: large enough to recover hybrid's top-5 losses —
everything we lost in cycle 2 was still within the top 30 — small
enough to keep CPU latency tolerable).
"""

from __future__ import annotations

TOP_N = 30

_model = None


def get_reranker():
    """Lazy singleton — ~2.3 GB weights, fp32 on CPU."""
    global _model
    if _model is None:
        from FlagEmbedding import FlagReranker

        _model = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=False)
    return _model


def rerank(query: str, candidates: list[dict], k: int, scorer=None) -> list[dict]:
    """Reorder candidates by cross-encoder score, return top-k.

    `scorer` is injectable for tests; production uses the FlagReranker.
    """
    if not candidates:
        return []
    if scorer is None:
        model = get_reranker()

        def model_scorer(pairs: list[list[str]]) -> list[float]:
            raw = model.compute_score(pairs)
            return raw if isinstance(raw, list) else [raw]

        scorer = model_scorer

    scores = scorer([[query, c["text"]] for c in candidates])
    order = sorted(range(len(candidates)), key=lambda i: scores[i], reverse=True)
    return [{**candidates[i], "score": float(scores[i])} for i in order[:k]]


class RerankedRetriever:
    """Same .search() contract as DenseIndex/HybridRetriever.

    `scorer` is injectable for tests; None means the real cross-encoder.
    """

    def __init__(self, base, top_n: int = TOP_N, scorer=None) -> None:
        self.base = base
        self.top_n = top_n
        self.scorer = scorer

    def search(self, query: str, k: int = 10) -> list[dict]:
        candidates = self.base.search(query, k=self.top_n)
        return rerank(query, candidates, k=k, scorer=self.scorer)
