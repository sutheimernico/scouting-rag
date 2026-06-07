"""Answer generation via local Ollama (cycle 1) + closed-book mode (cycle −1).

The RAG prompt is strictly context-bound (basis for faithfulness
measurement); the closed-book prompt has no context and is the
parametric-knowledge reference line every RAG cycle must beat.
"""

from __future__ import annotations

import os
from pathlib import Path

import ollama
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "qwen2.5:7b")
VLM_MODEL = os.getenv("VLM_MODEL", "qwen2.5vl:7b")

# k=5 contexts à ~400 tokens + prompt fits comfortably; larger num_ctx
# would slow CPU prefill for no benefit at this k
NUM_CTX = 4096

RAG_PROMPT = """Du bist ein Fußball-Scouting-Assistent. Beantworte die Frage \
ausschließlich auf Basis der folgenden Kontextauszüge. Wenn die Antwort nicht \
im Kontext steht, sage genau das ("Dazu finde ich nichts im Korpus."). Erfinde \
nichts, nutze kein Vorwissen. Antworte knapp auf Deutsch und nenne Zahlen exakt \
so, wie sie im Kontext stehen.

KONTEXT:
{context}

FRAGE: {query}

ANTWORT:"""

CLOSED_BOOK_PROMPT = """Du bist ein Fußball-Scouting-Assistent. Beantworte die \
Frage aus deinem Wissen. Wenn du es nicht sicher weißt, sage das ehrlich. \
Antworte knapp auf Deutsch.

FRAGE: {query}

ANTWORT:"""


def _client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_HOST)


def _generate(prompt: str, model: str = GENERATOR_MODEL) -> dict:
    response = _client().generate(
        model=model,
        prompt=prompt,
        options={"num_ctx": NUM_CTX, "temperature": 0.0, "seed": 42},
    )
    return {
        "text": response["response"].strip(),
        "eval_count": response.get("eval_count"),
        "prompt_eval_count": response.get("prompt_eval_count"),
        "total_duration_s": round(response.get("total_duration", 0) / 1e9, 2),
    }


def generate_rag(query: str, contexts: list[str]) -> dict:
    context_block = "\n\n---\n\n".join(contexts)
    return _generate(RAG_PROMPT.format(context=context_block, query=query))


def generate_closed_book(query: str) -> dict:
    return _generate(CLOSED_BOOK_PROMPT.format(query=query))


VISUAL_PROMPT = """Du bist ein Fußball-Scouting-Assistent. Beantworte die Frage \
ausschließlich anhand der gezeigten Statblätter. Lies Werte und Perzentile exakt \
ab. Wenn die Antwort nicht ablesbar ist, sage genau das. Antworte knapp auf Deutsch.

FRAGE: {query}

ANTWORT:"""


def generate_visual(query: str, image_paths: list[str]) -> dict:
    """Answer from retrieved stat-sheet images via the local VLM (cycle 5)."""
    response = _client().generate(
        model=VLM_MODEL,
        prompt=VISUAL_PROMPT.format(query=query),
        images=image_paths,
        options={"num_ctx": NUM_CTX, "temperature": 0.0, "seed": 42},
    )
    return {
        "text": response["response"].strip(),
        "total_duration_s": round(response.get("total_duration", 0) / 1e9, 2),
    }


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "Wie viele Tore schoss Harry Kane 2025/26?"
    print(generate_closed_book(query))
