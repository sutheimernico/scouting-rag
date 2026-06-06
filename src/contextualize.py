"""Cycle 4: contextual retrieval — generate a situating sentence per chunk.

Anthropic-style contextual retrieval, adapted to CPU reality (documented
deviations): the context generator is qwen2.5:1.5b instead of the 7b
(7b would need days for 4,318 chunks; the task — one situating sentence —
is small-model-friendly), and the document context fed to the model is
capped instead of full documents.

Output: data/contextual/chunk_contexts.jsonl, one {"chunk_id", "context"}
per line. Resumable: existing chunk_ids are skipped, so the overnight run
survives interruptions.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import ollama
from dotenv import load_dotenv

from src.corpus import Chunk, load_corpus

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

OUT_FILE = REPO_ROOT / "data" / "contextual" / "chunk_contexts.jsonl"
ARTICLES_DIR = REPO_ROOT / "data" / "articles"

CONTEXT_MODEL = os.getenv("CONTEXT_MODEL", "qwen2.5:1.5b")
DOC_CAP_CHARS = 1500  # prompt-size cap for CPU prefill

PROMPT = """Dokument-Anfang:
{doc_head}

Abschnitt aus diesem Dokument:
{chunk}

Schreibe genau EINEN kurzen deutschen Satz, der diesen Abschnitt für eine \
Suchmaschine einordnet (wer/was, welches Thema). Nutze AUSSCHLIESSLICH \
Informationen, die oben stehen — erfinde keine Jahreszahlen, Saisons oder \
Fakten. Wenn etwas nicht im Text steht, lass es weg. Keine Einleitung, nur \
der Satz."""

_doc_heads: dict[str, str] = {}


def doc_head_for(chunk: Chunk) -> str:
    """Capped document opening: article text head, or table label + columns."""
    if chunk.doc_id in _doc_heads:
        return _doc_heads[chunk.doc_id]
    if chunk.source_class == "article":
        doc = json.loads((REPO_ROOT / "data" / chunk.doc_id).read_text(encoding="utf-8"))
        head = f"{doc.get('title') or ''}\n{(doc.get('text') or '')[:DOC_CAP_CHARS]}"
    else:
        # table chunks: label + header is already the best "document head"
        header = chunk.text.split(" | ", 1)[0]
        head = f"Tabelle: {header}"
    _doc_heads[chunk.doc_id] = head
    return head


def build_prompt(chunk: Chunk) -> str:
    return PROMPT.format(doc_head=doc_head_for(chunk), chunk=chunk.text[:1200])


def load_done() -> set[str]:
    if not OUT_FILE.exists():
        return set()
    return {
        json.loads(line)["chunk_id"]
        for line in OUT_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    # documented cycle decision: only article chunks get LLM contexts.
    # Table rows already carry their label/header context, and the 1.5b
    # model demonstrably degrades them (hallucinated rank/season claims
    # in the smoke test). The plan's target — context-less chunks — means
    # article middles here.
    chunks = [c for c in load_corpus() if c.source_class == "article"]
    done = load_done()
    todo = [c for c in chunks if c.chunk_id not in done]
    print(f"{len(done)} done, {len(todo)} to go (model: {CONTEXT_MODEL})", flush=True)

    client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    t0 = time.monotonic()
    with OUT_FILE.open("a", encoding="utf-8") as fh:
        for i, chunk in enumerate(todo, 1):
            response = client.generate(
                model=CONTEXT_MODEL,
                prompt=build_prompt(chunk),
                options={"num_ctx": 2048, "temperature": 0.0, "seed": 42, "num_predict": 60},
            )
            context = response["response"].strip().replace("\n", " ")
            fh.write(json.dumps({"chunk_id": chunk.chunk_id, "context": context}, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 100 == 0:
                rate = i / (time.monotonic() - t0)
                eta_h = (len(todo) - i) / rate / 3600
                print(f"  {i}/{len(todo)} ({rate:.1f}/s, eta {eta_h:.1f}h)", flush=True)
    print("all contexts generated", flush=True)


if __name__ == "__main__":
    main()
