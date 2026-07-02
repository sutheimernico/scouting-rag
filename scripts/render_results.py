#!/usr/bin/env python3
"""Regenerate the mechanically-derivable tables in results.md from eval/results/*.json.

`src/run_eval.py`'s docstring says results are "transferred to results.md
manually (with interpretation)". Manual transcription is an integrity risk
for a project whose whole point is honest, reproducible numbers — spot
checks while building this script found transcription drift in the
existing Precision@5 sub-table (see the correction note printed right
below that table in results.md). This script removes that risk for
everything that IS mechanically derivable from the JSON files:

- the five primary IR-metric tables (Recall@5, Recall@10, Precision@5,
  MRR, nDCG@10)
- the number-hit / faithful / honest / refusal-rate columns of the
  secondary generation-quality table

What stays hand-authored (deliberately, outside the marked blocks): the
"Manual check" column of the secondary table (a one-off human/Claude
review, not derivable from any JSON), the effective-recall-ceiling
analysis, cost/latency (indexing time and infra notes live nowhere in the
JSON), and every per-cycle delta/verdict paragraph — all interpretation,
not mechanical transform.

Trade-off, documented rather than silently kept: the previous manual
tables bolded "notable" values and annotated some cells (e.g. "0.67
(±0)"). That was editorial judgment, not part of the metric, and isn't
reproduced here — regenerating will drop such inline styling. Emphasis
belongs in the prose verdict blocks, which this script never touches.

Sections are marked with `<!-- auto:<name>:start -->` / `:end` HTML
comments in results.md; this script only ever replaces the text between an
existing marker pair (idempotent: re-running with unchanged JSON input
reproduces byte-identical output). It does not create new sections.

    python -m scripts.render_results          # write results.md in place
    python -m scripts.render_results --check  # exit 1 if regenerating would change the file
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "eval" / "results"
RESULTS_MD = REPO_ROOT / "results.md"

# Per-cycle metadata. `retrieval_file` / `secondary_file` are the canonical
# source for that cycle's row — where a cycle produced more than one
# retrieval run (e.g. cycle 3's dense+rerank ablation), the file used here
# is the one results.md has always reported as "the" cycle-N number.
CYCLE_ORDER = ["-1", "1", "2", "3", "4", "5", "6"]

CYCLES: dict[str, dict] = {
    "-1": dict(label="Closed book (no retrieval)", retrieval_file=None, secondary_file="cycle_minus1_closedbook_secondary.json", na=True),
    "1": dict(label="Naive dense (BGE-M3)", retrieval_file="cycle1_dense_retrieval.json", secondary_file="cycle1_rag_k5_secondary.json"),
    "2": dict(label="+ Hybrid (sparse + RRF)", retrieval_file="cycle2_hybrid_retrieval.json", secondary_file="cycle2_rag_hybrid_k5_secondary.json"),
    "3": dict(label="+ Reranking (cross-encoder)", retrieval_file="cycle3_hybrid_rerank_retrieval.json", secondary_file="cycle3_rag_dense_rerank_k5_secondary.json"),
    "4": dict(label="+ Contextual retrieval", retrieval_file="cycle4_dense_ctx_rerank_retrieval.json", secondary_file=None),
    "5": dict(label="Visual (ColQwen)", retrieval_file="cycle5_visual_retrieval.json", secondary_file="cycle5_visual_rag_k5_secondary.json"),
    "6": dict(label="Agentic (optional)", retrieval_file=None, secondary_file=None),
}

COLUMNS = [("global", "global"), ("semantic", "semantic"), ("exact_match", "exact-match"), ("multi_hop", "multi-hop"), ("visual", "visual")]

METRIC_TABLES = [
    ("recall5", "recall@5", True),
    ("recall10", "recall@10", False),
    ("precision5", "precision@5", False),
    ("mrr", "mrr", False),
    ("ndcg10", "ndcg@10", False),
]

SUBSET_LABEL = {"global": "global", "exact_match": "exact-match", "semantic": "semantic", "multi_hop": "multi-hop", "visual": "visual"}

# Not derivable from any JSON — a one-off human/Claude review sample.
# Update by hand if a new manual review is done for another cycle.
MANUAL_CHECK_NOTES = {
    "-1": "–",
    "1": "done (Claude, not human — see below)",
    "2": "–",
    "3": "–",
}


def load_json(name: str | None) -> dict | None:
    if name is None:
        return None
    path = RESULTS_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: float | None, bold: bool = False) -> str:
    if value is None:
        return "n/a"
    text = f"{value:.2f}"
    return f"**{text}**" if bold else text


def render_metric_table(metric_key: str, always_show_all: bool) -> str:
    header = "| Cycle | Technique | " + " | ".join(c[1] for c in COLUMNS) + " |"
    sep = "|" + "---|" * (2 + len(COLUMNS))
    rows = [header, sep]
    for cid in CYCLE_ORDER:
        cfg = CYCLES[cid]
        data = load_json(cfg["retrieval_file"])
        if data is None:
            if not always_show_all:
                continue
            cells = ["–"] * len(COLUMNS) if cfg.get("na") else [""] * len(COLUMNS)
        else:
            metrics = data["metrics"]
            cells = [fmt(metrics.get(col, {}).get(metric_key)) for col, _ in COLUMNS]
        rows.append(f"| {cid} | {cfg['label']} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def render_secondary_table() -> str:
    header = "| Cycle | Number-hit exact-match (n=18) | Faithful strict (n=59) | Honest (n=59) | Refusal rate | Manual check (n=13) |"
    sep = "|---|---|---|---|---|---|"
    rows = [header, sep]
    for cid in CYCLE_ORDER:
        cfg = CYCLES[cid]
        data = load_json(cfg["secondary_file"])
        if data is None:
            continue
        number_hit_key = next((k for k in data if k.startswith("number_hit_")), None)
        subset = number_hit_key.removeprefix("number_hit_") if number_hit_key else None
        nh = data.get(number_hit_key, {}) if number_hit_key else {}
        hit_rate = nh.get("hit_rate")
        nh_cell = fmt(hit_rate, bold=True)
        if subset and subset != "exact_match" and hit_rate is not None:
            nh_cell += f" ({SUBSET_LABEL.get(subset, subset)})"
        faith = data.get("faithfulness")
        if faith is None:
            faithful_cell, honest_cell, refusal_cell = "n/a (no context to be faithful to)", "n/a", "–"
        else:
            details = faith["details"]
            honest = sum(1 for d in details if d["supported"] or d["refusal"]) / len(details)
            faithful_cell = fmt(faith["faithful_rate"])
            honest_cell = fmt(round(honest, 4))
            refusal_cell = fmt(faith["refusal_rate"])
        manual_cell = MANUAL_CHECK_NOTES.get(cid, "–")
        rows.append(f"| {cid} | {nh_cell} | {faithful_cell} | {honest_cell} | {refusal_cell} | {manual_cell} |")
    return "\n".join(rows)


SECTION_RENDERERS = {f"auto:{name}": (lambda mk=metric_key, all_=always: render_metric_table(mk, all_)) for name, metric_key, always in METRIC_TABLES}
SECTION_RENDERERS["auto:secondary"] = render_secondary_table


def splice(content: str, marker: str, body: str) -> str:
    """Replace everything between a marker's start/end comments with `body`.

    Tolerates both the empty starting state (`start -->\\n<!-- end -->`, no
    blank line) and an already-populated block, so the same function bootstraps
    a brand-new marker pair and re-renders an existing one identically.
    """
    pattern = re.compile(
        rf"<!-- {re.escape(marker)}:start -->\n?.*?\n?<!-- {re.escape(marker)}:end -->",
        re.DOTALL,
    )
    if not pattern.search(content):
        raise ValueError(f"marker not found in results.md: {marker}")
    replacement = f"<!-- {marker}:start -->\n{body}\n<!-- {marker}:end -->"
    return pattern.sub(lambda _: replacement, content, count=1)


def render(content: str) -> str:
    for marker, renderer in SECTION_RENDERERS.items():
        content = splice(content, marker, renderer())
    return content


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if regenerating would change results.md, without writing")
    args = parser.parse_args()

    original = RESULTS_MD.read_text(encoding="utf-8")
    updated = render(original)

    if args.check:
        if updated != original:
            print("results.md is stale — run `python -m scripts.render_results` to regenerate")
            sys.exit(1)
        print("results.md is up to date")
        return

    RESULTS_MD.write_text(updated, encoding="utf-8")
    print("wrote results.md" if updated != original else "results.md already up to date")


if __name__ == "__main__":
    main()
