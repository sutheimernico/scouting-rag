"""Judge-free retrieval metrics against golden-set ground truth (cycle 1).

Canonical implementation of the relevance rules from eval/SCHEMA.md:

- passage:   chunk text contains the quote (whitespace-normalized substring)
- table_row: chunk text contains all match_keys; purely numeric keys match
             on word boundaries in raw source representation
- image:     a text chunk can never satisfy it (text cycles measure this
             gap deliberately); the visual cycle passes retrieved page ids

Metrics (per query, then averaged globally and per type):

- recall@k:    covered ground-truth entries / all entries (multi-GT aware)
- precision@k: relevant retrieved / k (relevant = matches any GT entry)
- mrr:         1 / rank of first relevant chunk (0 if none in top-k)
- ndcg@k:      binary relevance, ideal = all GT entries ranked first
"""

from __future__ import annotations

import math
import re


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def key_in(key: str, text: str) -> bool:
    if re.fullmatch(r"[\d.,]+", key):
        return re.search(rf"(?<![\d.]){re.escape(key)}(?![\d.])", text) is not None
    return key in text


def chunk_matches_gt(chunk: dict, gt: dict) -> bool:
    """chunk: {'doc_id', 'text'} (or {'page_id'} in the visual cycle)."""
    if gt["kind"] == "image":
        return chunk.get("page_id") == gt["doc_id"]
    if chunk.get("doc_id") != gt["doc_id"]:
        return False
    if gt["kind"] == "passage":
        return norm_ws(gt["quote"]) in norm_ws(chunk.get("text", ""))
    if gt["kind"] == "table_row":
        return all(key_in(k, chunk.get("text", "")) for k in gt["match_keys"])
    raise ValueError(f"unknown ground-truth kind: {gt['kind']}")


def query_metrics(ground_truth: list[dict], retrieved: list[dict], ks: tuple[int, ...] = (5, 10)) -> dict:
    """Metrics for one query given its ranked retrieved chunks."""
    n_gt = len(ground_truth)
    # for each retrieved rank: which GT entries does it cover?
    covers: list[set[int]] = [
        {i for i, gt in enumerate(ground_truth) if chunk_matches_gt(chunk, gt)}
        for chunk in retrieved
    ]

    out: dict[str, float] = {}
    for k in ks:
        covered: set[int] = set()
        for c in covers[:k]:
            covered |= c
        out[f"recall@{k}"] = len(covered) / n_gt
        relevant_at_k = sum(1 for c in covers[:k] if c)
        out[f"precision@{k}"] = relevant_at_k / k

    first_rank = next((r + 1 for r, c in enumerate(covers) if c), None)
    out["mrr"] = 1.0 / first_rank if first_rank else 0.0

    k_ndcg = max(ks)
    dcg = sum(1.0 / math.log2(r + 2) for r, c in enumerate(covers[:k_ndcg]) if c)
    idcg = sum(1.0 / math.log2(r + 2) for r in range(min(n_gt, k_ndcg)))
    out[f"ndcg@{k_ndcg}"] = dcg / idcg if idcg else 0.0
    return out


def aggregate(per_query: list[dict], types: list[str]) -> dict:
    """Mean metrics globally and per question type. Reports n everywhere."""
    assert len(per_query) == len(types)
    metric_names = list(per_query[0].keys()) if per_query else []

    def mean_over(indices: list[int]) -> dict:
        return {
            "n": len(indices),
            **{
                m: round(sum(per_query[i][m] for i in indices) / len(indices), 4)
                for m in metric_names
            },
        }

    result = {"global": mean_over(list(range(len(per_query))))}
    for qtype in sorted(set(types)):
        result[qtype] = mean_over([i for i, t in enumerate(types) if t == qtype])
    return result
