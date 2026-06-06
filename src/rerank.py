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
BATCH_SIZE = 8  # CPU RAM-friendly
MODEL_NAME = "BAAI/bge-reranker-v2-m3"

_model = None
_tokenizer = None


def get_reranker():
    """Lazy singleton — ~2.3 GB weights, fp32 on CPU.

    Loaded via plain transformers (the documented HF path for
    bge-reranker): FlagEmbedding's FlagReranker wrapper is incompatible
    with our pinned transformers version (calls the removed
    tokenizer.prepare_for_model).
    """
    global _model, _tokenizer
    if _model is None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _model.eval()
        torch.set_grad_enabled(False)
    assert _model is not None and _tokenizer is not None
    return _model, _tokenizer


def rerank(query: str, candidates: list[dict], k: int, scorer=None) -> list[dict]:
    """Reorder candidates by cross-encoder score, return top-k.

    `scorer` is injectable for tests; production uses the FlagReranker.
    """
    if not candidates:
        return []
    if scorer is None:
        model, tokenizer = get_reranker()

        def model_scorer(pairs: list[list[str]]) -> list[float]:
            scores: list[float] = []
            for start in range(0, len(pairs), BATCH_SIZE):
                batch = pairs[start : start + BATCH_SIZE]
                inputs = tokenizer(
                    batch, padding=True, truncation=True, max_length=512, return_tensors="pt"
                )
                logits = model(**inputs).logits.view(-1)
                scores.extend(logits.float().tolist())
            return scores

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
