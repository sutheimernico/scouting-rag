"""Unit tests for tokenization and RRF fusion (no model loading)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.hybrid import rrf_fuse, tokenize


def test_tokenize_keeps_umlauts_numbers_and_abbreviations():
    assert tokenize("PPDA-Wert der Münchner: 9,3!") == ["ppda", "wert", "der", "münchner", "9", "3"]


def _item(cid: str) -> dict:
    return {"chunk_id": cid, "doc_id": f"doc/{cid}", "text": cid, "score": 0.0}


def test_rrf_rewards_presence_in_both_rankings():
    dense = [_item("a"), _item("b"), _item("c")]
    sparse = [_item("c"), _item("d"), _item("a")]
    fused = rrf_fuse([dense, sparse], k=4)
    ids = [f["chunk_id"] for f in fused]
    # a and c appear in both lists -> must outrank single-list b and d
    assert set(ids[:2]) == {"a", "c"}
    assert ids[0] == "a"  # rank 1 + rank 3 beats rank 3 + rank 1? equal -> tiebreak by dense
    assert fused[0]["score"] == pytest.approx(1 / 61 + 1 / 63)


def test_rrf_single_list_preserves_order_and_k():
    ranking = [_item(c) for c in "abcde"]
    fused = rrf_fuse([ranking], k=3)
    assert [f["chunk_id"] for f in fused] == ["a", "b", "c"]


def test_rrf_deterministic_tiebreak():
    dense = [_item("x"), _item("y")]
    sparse = [_item("y"), _item("x")]
    a = rrf_fuse([dense, sparse], k=2)
    b = rrf_fuse([dense, sparse], k=2)
    assert [f["chunk_id"] for f in a] == [f["chunk_id"] for f in b]
