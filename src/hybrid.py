"""Cycle 2: hybrid retrieval — BM25 sparse + dense, fused via RRF.

BM25 (rank_bm25, new pinned dependency — battle-tested Okapi
implementation; a hand-rolled one would add tokenization bug risk for
zero benefit) runs over the exact same chunks as the dense index, so the
cycle delta stays attributable to the retrieval technique alone.

Reciprocal rank fusion: score(d) = Σ_r 1 / (K + rank_r(d)), K=60
(standard from the original RRF paper). Both retrievers contribute their
top CANDIDATE_POOL ranks; ties resolve by dense rank for determinism.
"""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from src.corpus import Chunk, load_corpus
from src.embed_index import DenseIndex

RRF_K = 60
CANDIDATE_POOL = 50

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens; keeps umlauts and numbers ("ppda", "36")."""
    return _TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self._bm25 = BM25Okapi([tokenize(c.text) for c in chunks])

    def search(self, query: str, k: int = 10) -> list[dict]:
        scores = self._bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [
            {
                "chunk_id": self.chunks[i].chunk_id,
                "doc_id": self.chunks[i].doc_id,
                "text": self.chunks[i].text,
                "source_class": self.chunks[i].source_class,
                "score": float(scores[i]),
            }
            for i in order
        ]


def rrf_fuse(rankings: list[list[dict]], k: int = 10, rrf_k: int = RRF_K) -> list[dict]:
    """Fuse ranked lists of chunk dicts by chunk_id."""
    scores: dict[str, float] = {}
    first_seen: dict[str, dict] = {}
    tiebreak: dict[str, int] = {}
    for ranking_idx, ranking in enumerate(rankings):
        for rank, item in enumerate(ranking):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (rrf_k + rank + 1)
            if cid not in first_seen:
                first_seen[cid] = item
                tiebreak[cid] = ranking_idx * 10_000 + rank
    fused = sorted(scores, key=lambda cid: (-scores[cid], tiebreak[cid]))
    return [{**first_seen[cid], "score": scores[cid]} for cid in fused[:k]]


class HybridRetriever:
    """Same .search() contract as DenseIndex — drop-in for run_eval."""

    def __init__(self) -> None:
        self.dense = DenseIndex()
        self.bm25 = BM25Index(load_corpus())

    def search(self, query: str, k: int = 10) -> list[dict]:
        dense_ranking = self.dense.search(query, k=CANDIDATE_POOL)
        sparse_ranking = self.bm25.search(query, k=CANDIDATE_POOL)
        return rrf_fuse([dense_ranking, sparse_ranking], k=k)


if __name__ == "__main__":
    import sys

    retriever = HybridRetriever()
    for hit in retriever.search(" ".join(sys.argv[1:]) or "PPDA FC Bayern", k=5):
        print(f"  {hit['score']:.4f} [{hit['doc_id']}] {hit['text'][:100]}")
