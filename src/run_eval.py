"""Run the golden-set evaluation for a cycle.

Modes:
    retrieval    judge-free IR metrics over the golden set (fast, primary)
    closedbook   cycle −1: generate answers without retrieval (slow, CPU)
    rag          generate answers with top-k retrieved context (slow, CPU)

Results land in eval/results/<name>.json; the numbers are then transferred
to results.md manually (with interpretation) per the cycle report.

    python -m src.run_eval retrieval --name cycle1_dense
    python -m src.run_eval closedbook --name cycle_minus1
    python -m src.run_eval rag --name cycle1_rag --k 5
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN = REPO_ROOT / "eval" / "golden_set.jsonl"
RESULTS_DIR = REPO_ROOT / "eval" / "results"


def load_golden() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines()]


def run_retrieval() -> dict:
    from src.embed_index import DenseIndex
    from src.eval_metrics import aggregate, query_metrics

    index = DenseIndex()
    entries = load_golden()
    per_query, types, details = [], [], []
    t0 = time.monotonic()
    for entry in entries:
        retrieved = index.search(entry["query"], k=10)
        metrics = query_metrics(entry["ground_truth"], retrieved)
        per_query.append(metrics)
        types.append(entry["type"])
        details.append(
            {
                "id": entry["id"],
                "type": entry["type"],
                **{k: round(v, 4) for k, v in metrics.items()},
                "top_docs": [r["doc_id"] for r in retrieved[:5]],
            }
        )
        print(f"  {entry['id']} {entry['type']:<12} r@5={metrics['recall@5']:.2f} mrr={metrics['mrr']:.2f}", flush=True)
    elapsed = time.monotonic() - t0
    return {
        "mode": "retrieval",
        "latency_per_query_s": round(elapsed / len(entries), 2),
        "metrics": aggregate(per_query, types),
        "details": details,
    }


def _run_generation(args: argparse.Namespace, closed_book: bool) -> dict:
    from src.rag import generate_closed_book, generate_rag

    entries = load_golden()
    index = None
    if not closed_book:
        from src.embed_index import DenseIndex

        index = DenseIndex()
    outputs = []
    t0 = time.monotonic()
    for entry in entries:
        if closed_book or index is None:
            result = generate_closed_book(entry["query"])
            contexts_docs: list[str] = []
            context_texts: list[str] = []
        else:
            retrieved = index.search(entry["query"], k=args.k)
            context_texts = [r["text"] for r in retrieved]
            result = generate_rag(entry["query"], context_texts)
            contexts_docs = [r["doc_id"] for r in retrieved]
        outputs.append(
            {
                "id": entry["id"],
                "type": entry["type"],
                "query": entry["query"],
                "reference_answer": entry["reference_answer"],
                "answer": result["text"],
                "context_docs": contexts_docs,
                "context_texts": context_texts,  # judge needs the actual texts
                "duration_s": result["total_duration_s"],
            }
        )
        print(f"  {entry['id']} ({result['total_duration_s']}s): {result['text'][:80]!r}", flush=True)
    elapsed = time.monotonic() - t0
    return {
        "mode": "closedbook" if closed_book else f"rag_k{args.k}",
        "latency_per_query_s": round(elapsed / len(entries), 2),
        "outputs": outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["retrieval", "closedbook", "rag"])
    parser.add_argument("--name", required=True, help="output file name (eval/results/<name>.json)")
    parser.add_argument("--k", type=int, default=5, help="contexts for rag mode")
    args = parser.parse_args()

    if args.mode == "retrieval":
        result = run_retrieval()
    else:
        result = _run_generation(args, closed_book=(args.mode == "closedbook"))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"{args.name}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {out_path}")
    if "metrics" in result:
        print(json.dumps(result["metrics"], indent=1))


if __name__ == "__main__":
    main()
