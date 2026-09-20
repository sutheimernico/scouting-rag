"""Unit tests for the judge-free retrieval metrics (spec promise)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.eval_metrics import aggregate, chunk_matches_gt, query_metrics

GT_PASSAGE = {"doc_id": "articles/a.json", "kind": "passage", "quote": "der schnelle  Spieler"}
GT_ROW = {"doc_id": "stats/x.csv", "kind": "table_row", "match_keys": ["H. Kane", "36"]}
GT_IMAGE = {"doc_id": "statsheets/p.png", "kind": "image"}


def chunk(doc_id: str, text: str) -> dict:
    return {"doc_id": doc_id, "text": text}


class TestMatcher:
    def test_passage_matches_with_whitespace_normalization(self):
        assert chunk_matches_gt(chunk("articles/a.json", "xx der schnelle Spieler yy"), GT_PASSAGE)

    def test_passage_requires_same_doc(self):
        assert not chunk_matches_gt(chunk("articles/b.json", "der schnelle Spieler"), GT_PASSAGE)

    def test_table_row_needs_all_keys_with_numeric_word_boundary(self):
        assert chunk_matches_gt(chunk("stats/x.csv", "name: H. Kane | goals: 36"), GT_ROW)
        assert not chunk_matches_gt(chunk("stats/x.csv", "name: H. Kane | goals: 136"), GT_ROW)
        assert not chunk_matches_gt(chunk("stats/x.csv", "name: H. Kane"), GT_ROW)

    def test_image_unreachable_for_text_chunks_but_matches_page_id(self):
        assert not chunk_matches_gt(chunk("statsheets/p.png", "anything"), GT_IMAGE)
        assert chunk_matches_gt({"page_id": "statsheets/p.png"}, GT_IMAGE)


class TestQueryMetrics:
    def test_perfect_single_gt_at_rank_one(self):
        retrieved = [chunk("articles/a.json", "der schnelle Spieler")] + [
            chunk("articles/z.json", "noise")
        ] * 9
        m = query_metrics([GT_PASSAGE], retrieved)
        assert m["recall@5"] == 1.0
        assert m["mrr"] == 1.0
        assert m["ndcg@10"] == 1.0
        assert m["precision@5"] == pytest.approx(1 / 5)

    def test_miss_everywhere_is_all_zero(self):
        retrieved = [chunk("articles/z.json", "noise")] * 10
        m = query_metrics([GT_PASSAGE], retrieved)
        assert m["recall@5"] == m["recall@10"] == m["mrr"] == m["ndcg@10"] == 0.0

    def test_multi_gt_partial_coverage(self):
        # one of two GT entries covered at rank 6 -> recall@5=0, recall@10=0.5
        retrieved = [chunk("articles/z.json", "noise")] * 5 + [
            chunk("stats/x.csv", "H. Kane | 36")
        ] + [chunk("articles/z.json", "noise")] * 4
        m = query_metrics([GT_ROW, GT_IMAGE], retrieved)
        assert m["recall@5"] == 0.0
        assert m["recall@10"] == 0.5
        assert m["mrr"] == pytest.approx(1 / 6)

    def test_ndcg_dedups_repeated_coverage_of_one_gt_entry(self):
        """Regression: several chunks may satisfy the SAME single GT entry.

        Before the fix DCG credited every covering rank while IDCG capped at
        min(n_gt, k)=1 slot, so nDCG@10 came out at 1 + 1/log2(3) = 1.6309.
        """
        retrieved = [
            chunk("articles/a.json", "der schnelle Spieler, Teil 1"),
            chunk("articles/a.json", "und der schnelle Spieler, Teil 2"),
        ] + [chunk("articles/z.json", "noise")] * 8
        m = query_metrics([GT_PASSAGE], retrieved)
        assert m["ndcg@10"] == pytest.approx(1.0)
        assert m["recall@10"] == 1.0

    def test_ndcg_multi_gt_skips_redundant_rank(self):
        """Redundant rank 2 earns no gain; rank 3's new GT entry does.

        dcg = 1/log2(2) + 1/log2(4) = 1.500000, idcg = 1/log2(2) + 1/log2(3)
        = 1.630930 -> 0.919721. Old code also credited rank 2 (1/log2(3)),
        giving dcg = 2.130930 and nDCG = 1.306555 > 1.
        """
        retrieved = [
            chunk("stats/x.csv", "H. Kane | 36"),
            chunk("stats/x.csv", "H. Kane | 36 (duplicate row chunk)"),
            chunk("articles/a.json", "der schnelle Spieler"),
        ] + [chunk("articles/z.json", "noise")] * 7
        m = query_metrics([GT_ROW, GT_PASSAGE], retrieved)
        assert m["ndcg@10"] == pytest.approx(0.9197208, abs=1e-6)
        assert m["recall@10"] == 1.0

    def test_ndcg_never_exceeds_one_on_worst_case_duplication(self):
        retrieved = [chunk("articles/a.json", "der schnelle Spieler")] * 10
        m = query_metrics([GT_PASSAGE], retrieved)
        assert m["ndcg@10"] <= 1.0

    def test_precision_at_k_is_item_wise_and_needs_no_dedup(self):
        """Precision counts retrieved items, not covered GT — dedup is wrong here.

        Both top-2 chunks really are relevant items, so precision@5 = 2/5 even
        though they cover the same single GT entry. Guards the write-up claim
        that only DCG was ever affected by the missing dedup.
        """
        retrieved = [
            chunk("articles/a.json", "der schnelle Spieler, Teil 1"),
            chunk("articles/a.json", "und der schnelle Spieler, Teil 2"),
        ] + [chunk("articles/z.json", "noise")] * 8
        m = query_metrics([GT_PASSAGE], retrieved)
        assert m["precision@5"] == pytest.approx(2 / 5)

    def test_visual_gt_zero_in_text_cycle_by_design(self):
        retrieved = [chunk("articles/z.json", "noise")] * 10
        m = query_metrics([GT_IMAGE], retrieved)
        assert m["recall@10"] == 0.0


class TestAggregate:
    def test_global_and_per_type_with_n(self):
        per_query = [
            {"recall@5": 1.0, "mrr": 1.0},
            {"recall@5": 0.0, "mrr": 0.0},
            {"recall@5": 0.5, "mrr": 0.5},
        ]
        agg = aggregate(per_query, ["semantic", "semantic", "visual"])
        assert agg["global"]["n"] == 3
        assert agg["global"]["recall@5"] == pytest.approx(0.5)
        assert agg["semantic"]["n"] == 2
        assert agg["semantic"]["recall@5"] == pytest.approx(0.5)
        assert agg["visual"]["recall@5"] == pytest.approx(0.5)
