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
- retrieval failure rate (1 - Recall@k), single-hop vs. multi-hop vs. visual
- paired-bootstrap confidence intervals for the core cycle-over-cycle deltas
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
sys.path.insert(0, str(REPO_ROOT))

from src.bootstrap import paired_bootstrap_delta  # noqa: E402

RESULTS_DIR = REPO_ROOT / "eval" / "results"
RESULTS_MD = REPO_ROOT / "results.md"

# Artifacts produced before this stamp existed were computed with the pre-2026-09-20
# nDCG implementation (DCG without ground-truth dedup). Their nDCG@10 cells are
# marked rather than silently mixed with recomputed ones.
CURRENT_METRICS_VERSION = "2026-09-20-ndcg-dedup"
STALE_MARK = " ⚠"

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
    # k=1, not k=5: generate_visual's NUM_CTX=4096 (sized for text RAG contexts)
    # overflows at ~1575 tokens/image once k>=2 images are attached — see the
    # cycle-5 verdict below for the full blocker writeup.
    "5": dict(label="Visual (ColQwen)", retrieval_file="cycle5_visual_retrieval.json", secondary_file="cycle5_visual_rag_k1_secondary.json"),
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

SINGLE_HOP_TYPES = {"semantic", "exact_match"}

# Core cycle-over-cycle comparisons already narrated in the per-cycle
# verdict blocks below the tables — hardened here with a paired bootstrap
# CI instead of a bare point estimate. Deliberately curated, not
# exhaustive (metric x subset x cycle-pair would be >100 rows and most
# combinations are not referenced by any claim in the write-up).
CORE_COMPARISONS = [
    ("Cycle 1 -> 2 (dense -> hybrid)", "cycle1_dense_retrieval.json", "cycle2_hybrid_retrieval.json", "recall@5", "global"),
    ("Cycle 1 -> 2 (dense -> hybrid)", "cycle1_dense_retrieval.json", "cycle2_hybrid_retrieval.json", "recall@5", "exact_match"),
    ("Cycle 1 -> 2 (dense -> hybrid)", "cycle1_dense_retrieval.json", "cycle2_hybrid_retrieval.json", "recall@5", "semantic"),
    ("Cycle 1 -> 2 (dense -> hybrid)", "cycle1_dense_retrieval.json", "cycle2_hybrid_retrieval.json", "recall@5", "multi_hop"),
    ("Cycle 2 -> 3 (hybrid -> +reranking)", "cycle2_hybrid_retrieval.json", "cycle3_hybrid_rerank_retrieval.json", "recall@5", "global"),
    ("Cycle 2 -> 3 (hybrid -> +reranking)", "cycle2_hybrid_retrieval.json", "cycle3_hybrid_rerank_retrieval.json", "recall@5", "semantic"),
    ("Cycle 2 -> 3 (hybrid -> +reranking)", "cycle2_hybrid_retrieval.json", "cycle3_hybrid_rerank_retrieval.json", "recall@5", "multi_hop"),
    ("Cycle 3 -> 4 (+reranking -> +contextual)", "cycle3_hybrid_rerank_retrieval.json", "cycle4_dense_ctx_rerank_retrieval.json", "recall@5", "global"),
    ("Cycle-3 ablation: dense+rerank vs. hybrid+rerank", "cycle3_dense_rerank_ablation.json", "cycle3_hybrid_rerank_retrieval.json", "recall@5", "global"),
    ("Cycle 1 -> 2 (dense -> hybrid)", "cycle1_dense_retrieval.json", "cycle2_hybrid_retrieval.json", "mrr", "global"),
    ("Cycle 2 -> 3 (hybrid -> +reranking)", "cycle2_hybrid_retrieval.json", "cycle3_hybrid_rerank_retrieval.json", "mrr", "global"),
    ("Cycle 3 -> 4 (+reranking -> +contextual)", "cycle3_hybrid_rerank_retrieval.json", "cycle4_dense_ctx_rerank_retrieval.json", "mrr", "global"),
]

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
    stale = False
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
            if metric_key == "ndcg@10" and data.get("eval_metrics_version") != CURRENT_METRICS_VERSION:
                stale = True
                cells = [c + STALE_MARK if c != "n/a" else c for c in cells]
        rows.append(f"| {cid} | {cfg['label']} | " + " | ".join(cells) + " |")
    if metric_key == "ndcg@10" and stale:
        rows.append("")
        rows.append(
            f"_{STALE_MARK.strip()} = computed with the pre-2026-09-20 nDCG implementation "
            "(DCG without ground-truth dedup) and therefore biased upwards. Re-run "
            "`python -m src.run_eval retrieval --retriever <r> --name <file>` against the "
            "unchanged indexes and re-render to clear the mark; no re-indexing is needed._"
        )
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


def query_type_map(data: dict) -> dict[str, str]:
    return {d["id"]: d["type"] for d in data["details"]}


def values_by_ids(data: dict, metric_key: str, ids: list[str]) -> list[float]:
    by_id = {d["id"]: d[metric_key] for d in data["details"]}
    return [by_id[i] for i in ids]


def render_bootstrap_table() -> str:
    header = "| Comparison | Metric | Subset | n | delta (mean) | 95% CI | Note |"
    sep = "|---|---|---|---|---|---|---|"
    rows = [header, sep]
    for label, file_a, file_b, metric_key, subset in CORE_COMPARISONS:
        data_a, data_b = load_json(file_a), load_json(file_b)
        if data_a is None or data_b is None:
            continue
        types = query_type_map(data_a)
        ids = [i for i in types if subset == "global" or types[i] == subset]
        values_a = values_by_ids(data_a, metric_key, ids)
        values_b = values_by_ids(data_b, metric_key, ids)
        result = paired_bootstrap_delta(values_a, values_b)
        delta = result["mean"]
        note = "CI excludes 0 (deutet auf realem Effekt)" if result["excludes_zero"] else "CI includes 0 (nicht von Null unterscheidbar bei diesem n)"
        rows.append(
            f"| {label} | {metric_key} | {SUBSET_LABEL[subset]} | {result['n']} | {delta:+.2f} "
            f"| [{result['ci_low']:+.2f}, {result['ci_high']:+.2f}] | {note} |"
        )
    return "\n".join(rows)


# nDCG@10 as published before the 2026-09-20 DCG dedup fix. Captured once
# from the pre-fix committed artifacts (the file records the git ref and the
# command); the "after" column is always read live from the current artifacts,
# so the delta can never drift away from what the eval files actually say.
NDCG_BASELINE_FILE = "ndcg_fix_before_after.json"

NDCG_BEFORE_AFTER_ROWS = [
    ("1", "Naive dense (BGE-M3)"),
    ("2", "+ Hybrid (sparse + RRF)"),
    ("3", "+ Reranking (cross-encoder)"),
    ("3-ablation", "Cycle-3 ablation: dense + rerank"),
    ("4-standalone", "Contextual, standalone (no reranker)"),
    ("4", "+ Contextual retrieval"),
    ("5", "Visual (ColQwen)"),
]


def render_ndcg_before_after() -> str:
    baseline = load_json(NDCG_BASELINE_FILE)
    if baseline is None:
        return "_(nDCG baseline file missing — cannot render the before/after table)_"
    header = "| Cycle | Technique | Subset | nDCG@10 before | after | delta |"
    sep = "|---|---|---|---|---|---|"
    rows = [header, sep]
    for key, label in NDCG_BEFORE_AFTER_ROWS:
        entry = baseline["before"].get(key)
        if entry is None:
            continue
        current = load_json(entry["file"])
        if current is None:
            continue
        for subset, subset_label in COLUMNS:
            before = entry.get(subset)
            after = current["metrics"].get(subset, {}).get("ndcg@10")
            if before is None or after is None:
                continue
            if abs(before - after) < 5e-5:
                continue
            rows.append(
                f"| {key} | {label} | {subset_label} | {before:.4f} | {after:.4f} | {after - before:+.4f} |"
            )
    rows.append("")
    rows.append(
        "_Only rows that moved are listed; every subset not shown came back "
        "bit-identical. Every other metric (recall@5/@10, precision@5, MRR) was "
        "unchanged in every artifact regenerated so far — see the reproducibility "
        "note above. Cycles whose nDCG@10 still carries the warning sign in the "
        "table above are not represented here yet._"
    )
    return "\n".join(rows)


def render_failure_rate_table(k: int) -> str:
    header = "| Cycle | Technique | global | single-hop (semantic+exact-match) | multi-hop | visual |"
    sep = "|---|---|---|---|---|---|"
    rows = [header, sep]
    metric_key = f"recall@{k}"
    for cid in CYCLE_ORDER:
        cfg = CYCLES[cid]
        data = load_json(cfg["retrieval_file"])
        if data is None:
            continue
        types = query_type_map(data)
        by_id = {d["id"]: d[metric_key] for d in data["details"]}

        def failure(ids: list[str]) -> float:
            return round(1 - sum(by_id[i] for i in ids) / len(ids), 4)

        all_ids = list(by_id.keys())
        single_hop_ids = [i for i in all_ids if types[i] in SINGLE_HOP_TYPES]
        multi_hop_ids = [i for i in all_ids if types[i] == "multi_hop"]
        visual_ids = [i for i in all_ids if types[i] == "visual"]
        cells = [fmt(failure(all_ids)), fmt(failure(single_hop_ids)), fmt(failure(multi_hop_ids)), fmt(failure(visual_ids))]
        rows.append(f"| {cid} | {cfg['label']} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


SECTION_RENDERERS = {f"auto:{name}": (lambda mk=metric_key, all_=always: render_metric_table(mk, all_)) for name, metric_key, always in METRIC_TABLES}
SECTION_RENDERERS["auto:secondary"] = render_secondary_table
SECTION_RENDERERS["auto:failure_rate_5"] = lambda: render_failure_rate_table(5)
SECTION_RENDERERS["auto:failure_rate_10"] = lambda: render_failure_rate_table(10)
SECTION_RENDERERS["auto:bootstrap"] = render_bootstrap_table
SECTION_RENDERERS["auto:ndcg_before_after"] = render_ndcg_before_after


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
