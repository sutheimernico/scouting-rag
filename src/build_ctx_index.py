"""Cycle 4: build the contextualized dense index.

Article chunks get their generated situating sentence prepended
(context + newline + original text); table chunks stay unchanged (they
already carry label context — see contextualize.py). Embedded into a
separate Qdrant collection so cycle 3 and cycle 4 stay comparable side
by side.

The payload text is the full indexed text (context + original), so the
golden-set passage quotes remain substrings and the eval matcher works
unchanged.

    python -m src.build_ctx_index
"""

from __future__ import annotations

import json
import time
from dataclasses import replace
from pathlib import Path

from src.corpus import Chunk, load_corpus
from src.embed_index import DenseIndex

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXTS_FILE = REPO_ROOT / "data" / "contextual" / "chunk_contexts.jsonl"
CTX_COLLECTION = "scouting_dense_ctx_v1"


def load_contexts() -> dict[str, str]:
    contexts: dict[str, str] = {}
    for line in CONTEXTS_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entry = json.loads(line)
            contexts[entry["chunk_id"]] = entry["context"]
    return contexts


def contextualized_corpus() -> list[Chunk]:
    contexts = load_contexts()
    chunks = load_corpus()
    out: list[Chunk] = []
    missing = 0
    for chunk in chunks:
        ctx = contexts.get(chunk.chunk_id)
        if chunk.source_class == "article" and ctx:
            out.append(replace(chunk, text=f"{ctx}\n{chunk.text}"))
        else:
            if chunk.source_class == "article":
                missing += 1
            out.append(chunk)
    if missing:
        print(f"WARNING: {missing} article chunks without context (run contextualize first)")
    return out


def main() -> None:
    chunks = contextualized_corpus()
    print(f"building contextualized index over {len(chunks)} chunks -> {CTX_COLLECTION}")
    t0 = time.monotonic()
    DenseIndex(collection=CTX_COLLECTION).build(chunks)
    print(f"done in {time.monotonic() - t0:.0f}s")


if __name__ == "__main__":
    main()
