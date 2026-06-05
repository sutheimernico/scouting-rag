"""Unit tests for chunking + the golden-set coverage integration test.

The integration test is the load-bearing one: it proves that every
golden-set ground truth (passages and table rows) is actually reachable
in the chunks the indexer will see. If chunking parameters ever split a
quote across boundaries, this fails loudly instead of silently capping
recall.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.corpus import chunk_text, csv_row_chunks, load_corpus, n_tokens, split_sentences

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN = REPO_ROOT / "eval" / "golden_set.jsonl"


def test_split_sentences_basic():
    text = "Erster Satz. Zweiter Satz! Dritter Satz? Vierter."
    assert len(split_sentences(text)) == 4


def test_chunk_text_respects_target_size():
    sentence = "Dies ist ein Beispielsatz mit einigen Wörtern für den Test. "
    text = sentence * 200
    chunks = chunk_text(text, target_tokens=400, overlap_ratio=0.15)
    assert len(chunks) > 1
    # chunks may overshoot by at most one sentence
    assert all(n_tokens(c) <= 400 + n_tokens(sentence) + 5 for c in chunks)


def test_chunk_text_overlap_carries_sentences():
    sentence = "Satz Nummer {} mit etwas Inhalt darin."
    text = " ".join(sentence.format(i) for i in range(120))
    chunks = chunk_text(text, target_tokens=200, overlap_ratio=0.15)
    for a, b in zip(chunks, chunks[1:]):
        # consecutive chunks share at least one sentence
        last_sentence = a.split(". ")[-1].strip(". ")
        assert last_sentence in b


def test_csv_row_chunks_preserve_raw_numeric_format(tmp_path, monkeypatch):
    import src.corpus as corpus_mod

    csv = tmp_path / "stats" / "x.csv"
    csv.parent.mkdir(parents=True)
    csv.write_text("Player,PrgP\nJoshua Kimmich,362.0\n", encoding="utf-8")
    monkeypatch.setattr(corpus_mod, "DATA", tmp_path)
    monkeypatch.setitem(corpus_mod.TABLE_LABELS, "stats/x.csv", "test table")
    [chunk] = csv_row_chunks("stats/x.csv")
    assert "PrgP: 362.0" in chunk.text  # not "362" — raw format preserved
    assert chunk.doc_id == "stats/x.csv"


# --- integration: golden set must be reachable in real chunks ---


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _key_in(key: str, text: str) -> bool:
    if re.fullmatch(r"[\d.,]+", key):
        return re.search(rf"(?<![\d.]){re.escape(key)}(?![\d.])", text) is not None
    return key in text


def test_every_golden_ground_truth_is_reachable_in_chunks():
    chunks = load_corpus()
    by_doc: dict[str, list] = {}
    for c in chunks:
        by_doc.setdefault(c.doc_id, []).append(c)

    missing: list[str] = []
    for line in GOLDEN.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        for gt in entry["ground_truth"]:
            if gt["kind"] == "image":
                continue  # visual ground truth is unreachable in text cycles by design
            doc_chunks = by_doc.get(gt["doc_id"], [])
            if gt["kind"] == "passage":
                ok = any(_norm(gt["quote"]) in _norm(c.text) for c in doc_chunks)
            else:  # table_row
                ok = any(all(_key_in(k, c.text) for k in gt["match_keys"]) for c in doc_chunks)
            if not ok:
                missing.append(f"{entry['id']}: {gt['kind']} in {gt['doc_id']}")

    assert not missing, f"golden ground truth unreachable in chunks: {missing}"
