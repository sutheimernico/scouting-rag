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

# Provenance stamp for the metric implementation an artifact was produced with.
# Bumped whenever src/eval_metrics.py changes a metric definition, so a result
# file always says which version computed it and the rendering scripts can flag
# tables that mix versions. Artifacts without the field predate 2026-09-20.
EVAL_METRICS_VERSION = "2026-09-20-ndcg-dedup"


def load_golden() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines()]


def make_retriever(name: str):
    if name == "dense":
        from src.embed_index import DenseIndex

        return DenseIndex()
    if name == "hybrid":
        from src.hybrid import HybridRetriever

        return HybridRetriever()
    if name == "dense_ctx":
        from src.build_ctx_index import CTX_COLLECTION
        from src.embed_index import DenseIndex

        return DenseIndex(collection=CTX_COLLECTION)
    if name == "visual":
        from src.visual_index import VisualIndex

        return VisualIndex()
    if name.endswith("_rerank"):
        from src.rerank import RerankedRetriever

        return RerankedRetriever(make_retriever(name.removesuffix("_rerank")))
    raise SystemExit(f"unknown retriever: {name}")


def run_retrieval(retriever_name: str) -> dict:
    from src.eval_metrics import aggregate, query_metrics

    index = make_retriever(retriever_name)
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
        "mode": f"retrieval_{retriever_name}",
        "eval_metrics_version": EVAL_METRICS_VERSION,
        "latency_per_query_s": round(elapsed / len(entries), 2),
        "metrics": aggregate(per_query, types),
        "details": details,
    }


def _run_generation(args: argparse.Namespace, closed_book: bool) -> dict:
    from src.rag import generate_closed_book, generate_rag, generate_visual

    visual = args.retriever == "visual"
    entries = load_golden()
    index = None if closed_book else make_retriever(args.retriever)
    # The visual cycle only generates over the visual subset: text queries have
    # no image ground truth, and the VLM has nothing to read for them.
    if visual:
        entries = [e for e in entries if e["type"] == "visual"]
    outputs = []
    t0 = time.monotonic()
    for entry in entries:
        if closed_book or index is None:
            result = generate_closed_book(entry["query"])
            contexts_docs: list[str] = []
            context_texts: list[str] = []
        elif visual:
            retrieved = index.search(entry["query"], k=args.k)
            contexts_docs = [r["page_id"] for r in retrieved]
            # page_id is "statsheets/<file>"; the VLM reads the image files directly
            image_paths = [str(REPO_ROOT / "data" / d) for d in contexts_docs]
            result = generate_visual(entry["query"], image_paths)
            context_texts = []  # no text context; faithfulness judge N/A, number-hit applies
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
        "mode": "closedbook" if closed_book else f"rag_{args.retriever}_k{args.k}",
        "latency_per_query_s": round(elapsed / len(entries), 2),
        "outputs": outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["retrieval", "closedbook", "rag"])
    parser.add_argument("--name", required=True, help="output file name (eval/results/<name>.json)")
    parser.add_argument("--k", type=int, default=5, help="contexts for rag mode")
    parser.add_argument(
        "--retriever",
        default="dense",
        choices=[
            "dense", "hybrid", "hybrid_rerank", "dense_rerank",
            "dense_ctx", "dense_ctx_rerank", "visual",
        ],
    )
    args = parser.parse_args()

    if args.mode == "retrieval":
        result = run_retrieval(args.retriever)
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
