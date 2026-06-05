#!/usr/bin/env python3
"""Measure corpus size in tokens for CORPUS.md (cycle-0 long-context check).

Token counts use tiktoken cl100k_base as a documented proxy (±10-15% vs.
the actual generator tokenizer). Stats CSVs are counted as raw text — the
markdown chunk conversion only exists from cycle 1 on; the proxy nature is
documented in CORPUS.md. Stat-sheet PNGs have no text tokens; they are
counted as pages (VLM image cost is a cycle-5 concern).
"""

from __future__ import annotations

import json
from pathlib import Path

import tiktoken

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "data" / "articles"
STATS_DIR = REPO_ROOT / "data" / "stats"
SHEETS_DIR = REPO_ROOT / "data" / "statsheets"

ENC = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(ENC.encode(text))


def summarize() -> dict:
    articles = [p for p in ARTICLES_DIR.glob("*.json") if not p.name.startswith("_")]
    article_tokens = 0
    article_words = 0
    per_source: dict[str, dict] = {}
    for path in articles:
        doc = json.loads(path.read_text(encoding="utf-8"))
        tokens = count_tokens(doc.get("text") or "")
        article_tokens += tokens
        article_words += len((doc.get("text") or "").split())
        src = per_source.setdefault(doc.get("source", "?"), {"docs": 0, "tokens": 0})
        src["docs"] += 1
        src["tokens"] += tokens

    csv_files = sorted(STATS_DIR.glob("**/*.csv"))
    csv_tokens = sum(count_tokens(p.read_text(encoding="utf-8")) for p in csv_files)

    sheets = [p for p in SHEETS_DIR.glob("*.png")]

    return {
        "articles": {
            "docs": len(articles),
            "words": article_words,
            "tokens": article_tokens,
            "per_source": per_source,
        },
        "stats_tables": {"files": len(csv_files), "tokens_raw_csv": csv_tokens},
        "statsheets": {"pages": len(sheets)},
        "text_tokens_total": article_tokens + csv_tokens,
    }


def main() -> None:
    summary = summarize()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
