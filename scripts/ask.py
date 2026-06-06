#!/usr/bin/env python3
"""Ask the scouting assistant a single question (interactive use).

    .venv/bin/python scripts/ask.py "Was sind die Schwächen von Marco Reus?"
    .venv/bin/python scripts/ask.py --retriever dense "..."        # fast (~0.4s retrieval)
    .venv/bin/python scripts/ask.py --show-context "..."           # inspect retrieved chunks

Default retriever is dense_rerank (the cycle-3 recommended stack,
~30 s retrieval on CPU) — use --retriever dense for quick playing.
Generation adds ~60–90 s on CPU either way.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag import generate_rag
from src.run_eval import make_retriever


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="your question")
    parser.add_argument(
        "--retriever", default="dense_rerank", choices=["dense", "hybrid", "hybrid_rerank", "dense_rerank"]
    )
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--show-context", action="store_true")
    args = parser.parse_args()
    query = " ".join(args.query)

    print(f"[retriever: {args.retriever}] retrieving ...", flush=True)
    t0 = time.monotonic()
    retriever = make_retriever(args.retriever)
    hits = retriever.search(query, k=args.k)
    t_retrieve = time.monotonic() - t0

    if args.show_context:
        for h in hits:
            print(f"\n--- {h['doc_id']} (score {h['score']:.3f}) ---\n{h['text'][:400]}")
        print()

    print(f"[{t_retrieve:.1f}s] generating ...", flush=True)
    result = generate_rag(query, [h["text"] for h in hits])

    print(f"\n{result['text']}\n")
    print("Quellen:")
    for doc_id in dict.fromkeys(h["doc_id"] for h in hits):
        print(f"  - {doc_id}")
    print(f"\n({t_retrieve:.1f}s retrieval, {result['total_duration_s']}s generation)")


if __name__ == "__main__":
    main()
