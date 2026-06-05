"""Corpus loading and chunking (cycle 1).

Two text chunk types feed the index:

- Article chunks: ~CHUNK_TOKENS tokens, sentence-respecting, with
  OVERLAP_RATIO token overlap so golden-set quotes cannot fall through
  chunk boundaries.
- Table row chunks: one CSV row -> one chunk ("header: value | ..."),
  read with dtype=str so the raw numeric representation of the source
  file is preserved exactly (binding rule in eval/SCHEMA.md — golden-set
  match_keys reference the raw format, e.g. "362.0").

Every chunk carries the doc_id of its source (path relative to data/),
which keeps the golden set chunking-agnostic.

Cycle-1 default decision (documented in the cycle report): 400-token
chunks, 15% overlap, cl100k tokenizer as sizing proxy.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import tiktoken

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / "data"

CHUNK_TOKENS = 400
OVERLAP_RATIO = 0.15

ENC = tiktoken.get_encoding("cl100k_base")

# human-readable context prepended to every row of a stats CSV
TABLE_LABELS = {
    "stats/openligadb/bundesliga_2025_table.csv": "Bundesliga Abschlusstabelle 2025/26 (final league table)",
    "stats/openligadb/bundesliga_2025_scorers.csv": "Bundesliga Torschützenliste 2025/26 (top scorers)",
    "stats/openligadb/2_bundesliga_2025_table.csv": "2. Bundesliga Abschlusstabelle 2025/26 (final league table)",
    "stats/openligadb/2_bundesliga_2025_scorers.csv": "2. Bundesliga Torschützenliste 2025/26 (top scorers)",
    "stats/fbref_wfr/bundesliga_2425_shooting.csv": "Bundesliga Spieler-Schussstatistik 2024/25 (player shooting stats)",
    "stats/fbref_wfr/bundesliga_2425_passing.csv": "Bundesliga Spieler-Passstatistik 2024/25 (player passing stats)",
    "stats/fbref_wfr/bundesliga_2425_playing_time.csv": "Bundesliga Spieler-Einsatzzeiten 2024/25 (player playing time)",
}

# pure noise for embeddings, never referenced by golden-set keys
DROP_COLUMNS = {"teamIconUrl", "Url", "goalGetterId", "teamInfoId"}


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str  # path relative to data/, matches golden-set doc_id
    text: str
    source_class: str  # "article" | "table"
    meta: dict = field(default_factory=dict)


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


def split_sentences(text: str) -> list[str]:
    """Pragmatic sentence split; imperfect on abbreviations, good enough
    for chunk sizing (boundaries only decide where chunks may end)."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ„\"0-9])", text)
    return [p for p in (s.strip() for s in parts) if p]


def chunk_text(text: str, target_tokens: int = CHUNK_TOKENS, overlap_ratio: float = OVERLAP_RATIO) -> list[str]:
    """Greedy sentence packing into ~target_tokens chunks with sentence overlap."""
    sentences = split_sentences(text)
    if not sentences:
        return []
    sent_tokens = [n_tokens(s) for s in sentences]
    chunks: list[str] = []
    current: list[int] = []  # sentence indices
    current_tok = 0
    i = 0
    while i < len(sentences):
        current.append(i)
        current_tok += sent_tokens[i]
        i += 1
        if current_tok >= target_tokens or i == len(sentences):
            chunks.append(" ".join(sentences[j] for j in current))
            if i == len(sentences):
                break
            # carry the trailing sentences worth ~overlap_ratio of the budget
            overlap_budget = int(target_tokens * overlap_ratio)
            carried: list[int] = []
            tok = 0
            for j in reversed(current):
                if tok + sent_tokens[j] > overlap_budget and carried:
                    break
                carried.insert(0, j)
                tok += sent_tokens[j]
                if tok >= overlap_budget:
                    break
            current = carried
            current_tok = tok
    return chunks


def load_articles() -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted((DATA / "articles").glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc_id = f"articles/{path.name}"
        title = doc.get("title") or ""
        body = doc.get("text") or ""
        # title prepended: helps retrieval, and golden quotes are body-only anyway
        for k, piece in enumerate(chunk_text(body)):
            text = f"{title}\n{piece}" if title else piece
            chunks.append(
                Chunk(
                    chunk_id=f"{doc['id']}#{k}",
                    doc_id=doc_id,
                    text=text,
                    source_class="article",
                    meta={"title": title, "source": doc.get("source"), "date": doc.get("date")},
                )
            )
    return chunks


def csv_row_chunks(rel_path: str) -> list[Chunk]:
    """One chunk per CSV row. dtype=str preserves raw numeric formats."""
    label = TABLE_LABELS.get(rel_path, rel_path)
    df = pd.read_csv(DATA / rel_path, dtype=str, keep_default_na=False)
    cols = [c for c in df.columns if c not in DROP_COLUMNS]
    chunks: list[Chunk] = []
    stem = Path(rel_path).stem
    for idx, row in df.iterrows():
        pairs = " | ".join(f"{c}: {row[c]}" for c in cols if row[c] != "")
        chunks.append(
            Chunk(
                chunk_id=f"{stem}#{idx}",
                doc_id=rel_path,
                text=f"{label} | {pairs}",
                source_class="table",
                meta={"table": stem, "row": int(idx)},
            )
        )
    return chunks


def load_tables() -> list[Chunk]:
    chunks: list[Chunk] = []
    for rel_path in TABLE_LABELS:
        chunks.extend(csv_row_chunks(rel_path))
    return chunks


def load_corpus() -> list[Chunk]:
    return load_articles() + load_tables()


if __name__ == "__main__":
    corpus = load_corpus()
    by_class: dict[str, int] = {}
    for c in corpus:
        by_class[c.source_class] = by_class.get(c.source_class, 0) + 1
    toks = sum(n_tokens(c.text) for c in corpus)
    print(f"{len(corpus)} chunks {by_class}, {toks:,} tokens total")
