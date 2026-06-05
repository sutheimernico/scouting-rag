"""Secondary generation metrics (cycle 1).

Two complementary signals, per design spec section 2:

1. answer_number_hit — judge-free, deterministic: does the generated
   answer contain the key numbers of the reference answer (word-boundary
   match)? Well-defined for the exact_match subset; reported alongside
   judge scores because it cannot be noisy.

2. judge_faithfulness — llama3.1:8b (different model family than the
   qwen generator) judges whether the answer is fully supported by the
   retrieved context. Judge noise is quantified once via test–retest
   with different seeds at temperature 0.3 and reported with every
   secondary metric (results.md).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import ollama
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "llama3.1:8b")

JUDGE_PROMPT = """You are a strict evaluator. Decide whether the ANSWER is fully \
supported by the CONTEXT. The answer counts as supported only if every factual \
claim in it appears in the context. An honest refusal ("nicht im Korpus" or \
similar) counts as supported=true with refusal=true. Respond with JSON only:
{{"supported": true|false, "refusal": true|false, "reason": "<one short sentence>"}}

CONTEXT:
{context}

QUESTION: {query}

ANSWER: {answer}

JSON:"""


def extract_numbers(text: str) -> list[str]:
    """Key numbers of a reference answer (handles 4.060 / 34,88 / 89 styles)."""
    return re.findall(r"\d+(?:[.,]\d+)*", text)


def answer_number_hit(answer: str, reference_answer: str) -> bool:
    """True iff every reference number appears in the answer.

    German formatting variants are normalized: 4.060 == 4060, 34,88 == 34.88.
    """

    def variants(num: str) -> set[str]:
        out = {num}
        out.add(num.replace(".", ""))  # thousands dot
        out.add(num.replace(",", "."))  # decimal comma -> dot
        out.add(num.replace(".", ","))
        return out

    refs = extract_numbers(reference_answer)
    if not refs:
        return False
    answer_nums = set()
    for n in extract_numbers(answer):
        answer_nums |= variants(n)
    return all(bool(variants(r) & answer_nums) for r in refs)


def judge_faithfulness(query: str, answer: str, contexts: list[str], *, seed: int = 42, temperature: float = 0.0) -> dict:
    client = ollama.Client(host=OLLAMA_HOST)
    prompt = JUDGE_PROMPT.format(context="\n\n---\n\n".join(contexts), query=query, answer=answer)
    response = client.generate(
        model=JUDGE_MODEL,
        prompt=prompt,
        options={"num_ctx": 4096, "temperature": temperature, "seed": seed},
        format="json",
    )
    try:
        verdict = json.loads(response["response"])
        return {
            "supported": bool(verdict.get("supported")),
            "refusal": bool(verdict.get("refusal")),
            "reason": str(verdict.get("reason", ""))[:200],
        }
    except (json.JSONDecodeError, TypeError):
        return {"supported": False, "refusal": False, "reason": "judge output unparseable"}
