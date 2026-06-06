"""Secondary metrics over a generation run (cycle 1).

Reads a generation result file (closedbook or rag mode), computes:

- number-hit rate on the exact_match subset (judge-free, deterministic)
- faithfulness via local judge over all answers (rag runs: against the
  retrieved contexts; closedbook runs: skipped — there is no context to
  be faithful to, only the number-hit applies)
- judge noise via test–retest (n=10, two seeds at temperature 0.3),
  measured once per cycle and reported next to every judge score

    python -m src.run_secondary eval/results/cycle1_rag_k5.json --judge
    python -m src.run_secondary eval/results/cycle_minus1_closedbook.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.judge import answer_number_hit, judge_faithfulness

REPO_ROOT = Path(__file__).resolve().parent.parent


def number_hit_rate(outputs: list[dict]) -> dict:
    subset = [o for o in outputs if o["type"] == "exact_match"]
    hits = [answer_number_hit(o["answer"], o["reference_answer"]) for o in subset]
    return {
        "n": len(subset),
        "hit_rate": round(sum(hits) / len(subset), 4) if subset else None,
        "misses": [o["id"] for o, h in zip(subset, hits) if not h],
    }


def faithfulness(outputs: list[dict], chunk_texts: dict[str, str] | None) -> dict:
    judged = []
    for o in outputs:
        contexts = o.get("context_texts") or []
        if not contexts and chunk_texts is not None:
            contexts = [chunk_texts.get(d, "") for d in o.get("context_docs", [])]
        verdict = judge_faithfulness(o["query"], o["answer"], contexts)
        judged.append({"id": o["id"], "type": o["type"], **verdict})
        print(f"  {o['id']} supported={verdict['supported']} refusal={verdict['refusal']}", flush=True)
    supported = sum(1 for j in judged if j["supported"])
    refusals = sum(1 for j in judged if j["refusal"])
    return {
        "n": len(judged),
        "faithful_rate": round(supported / len(judged), 4),
        "refusal_rate": round(refusals / len(judged), 4),
        "details": judged,
    }


def judge_noise(outputs: list[dict], n: int = 10) -> dict:
    """Test–retest agreement of the judge on the first n answers."""
    sample = outputs[:n]
    agree = 0
    for o in sample:
        contexts = o.get("context_texts") or []
        a = judge_faithfulness(o["query"], o["answer"], contexts, seed=1, temperature=0.3)
        b = judge_faithfulness(o["query"], o["answer"], contexts, seed=2, temperature=0.3)
        agree += a["supported"] == b["supported"]
    return {"n": n, "test_retest_agreement": round(agree / n, 4)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_file", type=Path)
    parser.add_argument("--judge", action="store_true", help="run faithfulness judge (slow)")
    parser.add_argument("--noise", action="store_true", help="run judge test-retest (slow)")
    args = parser.parse_args()

    data = json.loads(args.result_file.read_text(encoding="utf-8"))
    outputs = data["outputs"]
    summary: dict = {"source": args.result_file.name, "number_hit_exact_match": number_hit_rate(outputs)}

    if args.judge and data["mode"].startswith("rag"):
        summary["faithfulness"] = faithfulness(outputs, chunk_texts=None)
    if args.noise and data["mode"].startswith("rag"):
        summary["judge_noise"] = judge_noise(outputs)

    out_path = args.result_file.with_name(args.result_file.stem + "_secondary.json")
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "faithfulness"} |
                     ({"faithfulness": {k: v for k, v in summary["faithfulness"].items() if k != "details"}}
                      if "faithfulness" in summary else {}), indent=1))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
