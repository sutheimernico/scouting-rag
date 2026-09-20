#!/usr/bin/env python3
"""Generate the self-contained static study report at report/index.html.

Pulls the same numbers as results.md (via scripts/render_results, so the
two never drift on the metrics) plus a small amount of hand-curated
editorial content that lives only here: verdict badges, one-line "why",
and the cost/latency figures (not stored in any JSON — see
render_results.py's docstring for why cost/latency stays hand-authored).
Keep that content in sync with results.md by hand if a verdict changes.

No build step, no external resources: one HTML file, inline <style>,
charts as inline SVG (no JS, no CDN, no fonts/images fetched over the
network — works fully offline and under a strict CSP).

    python -m scripts.render_report
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from render_results import (  # noqa: E402
    CORE_COMPARISONS,
    CURRENT_METRICS_VERSION,
    CYCLE_ORDER,
    CYCLES,
    SINGLE_HOP_TYPES,
    SUBSET_LABEL,
    load_json,
    query_type_map,
)
from src.bootstrap import paired_bootstrap_delta  # noqa: E402

REPORT_DIR = REPO_ROOT / "report"
REPORT_PATH = REPORT_DIR / "index.html"

# Cycle 7 (GraphRAG) has no eval/results.md row (nothing was ever built,
# unlike cycle 6, which at least has a CYCLES entry) — labelled here only
# for the verdict card.
EXTRA_CYCLE_LABELS = {"7": "GraphRAG (optional)"}

# Column order for the subset charts — matches results.md's table columns
# (SUBSET_LABEL's dict order differs slightly and isn't meant as a display order).
SUBSET_ORDER = ["global", "semantic", "exact_match", "multi_hop", "visual"]

SERIES_COLOR = {
    "global": "#4f8ff7",
    "semantic": "#35c2a0",
    "exact_match": "#f2b84b",
    "multi_hop": "#f2665e",
    "visual": "#b18cf5",
}

# Editorial content: not derivable from any JSON, kept in sync with
# results.md / PROJECT.md by hand. verdict keys drive badge color+label.
VERDICT_META = {
    "keep": ("Keep", "#35c2a0"),
    "conditional": ("Keep, conditionally", "#f2b84b"),
    "drop": ("Drop", "#7c8592"),
    "pending": ("Needs Nico", "#4f8ff7"),
    "not_built": ("Not built (by design)", "#9b8cf5"),
    "closed": ("Closed — no verdict", "#e06c75"),
}

CYCLE_VERDICTS = {
    "-1": dict(verdict="keep", why="Baseline: without retrieval the generator gets 0/18 post-cutoff facts right — establishes the floor every later cycle must beat."),
    "1": dict(verdict="keep", why="The baseline. Naive dense retrieval already reaches semantic saturation (R@5=1.00); exact-match and multi-hop gaps are exactly what cycles 2/3 target."),
    "2": dict(verdict="conditional", why="Hybrid wins where the query carries specific tokens (exact-match, multi-hop) but regresses semantic@5 — the regression is designed to be healed by cycle 3's reranker."),
    "3": dict(verdict="keep", why="Strongest cycle: heals the cycle-2 regression and lifts every subset. Ablation shows dense+rerank ≡ hybrid+rerank — drop the fusion once a reranker is present. Recommended stack."),
    "4": dict(verdict="drop", why="Zero measurable delta over hybrid+rerank (bootstrap CI on the global recall@5 delta is a single point at 0) despite ~6h CPU cost for context generation. A clean negative result, not a failed cycle."),
    "5": dict(verdict="closed", why="Built, indexed (8.2h CPU) and evaluated — but the ColQwen2 checkpoint loads with its language backbone randomly initialized (colpali_engine/transformers key-naming drift, proven from the state dict). The measured 0.15 Recall@5 is a real number about a broken model, not about the technique. Closed without a technique verdict; evidence committed."),
    "6": dict(verdict="not_built", why="Trigger condition (multi-hop demonstrably weak) is met, but the cycle-3 finding is that the generator, not retrieval, is the end-to-end bottleneck past cycle 3 — decomposition would not move the measured metric."),
    "7": dict(verdict="not_built", why="Trigger condition (global cross-corpus provenance queries) does not occur anywhere in the golden set."),
}

# Cost/latency: not in any JSON (see render_results.py docstring) — hand-transcribed from results.md, keep in sync.
COST_LATENCY = [
    ("−1", "–", "~48s generation (closed book, no retrieval)", "Ollama"),
    ("1", "106 min (BGE-M3 encode, 4,318 chunks)", "0.43s retrieval + ~69s generation (7B CPU)", "Qdrant embedded"),
    ("2", "+ ~5s BM25 build (in-memory)", "0.38s retrieval + ~70s generation", "rank_bm25"),
    ("3", "– (reuses index)", "29.6s retrieval + ~65s generation (95s total)", "bge-reranker-v2-m3 (2.3 GB)"),
    ("4", "~6h context generation + 100 min re-encode", "unchanged", "– (cost bought nothing)"),
    ("5", "~8.2h visual index build (84 pages × ~350s)", "2.7s retrieval + ~106s VLM generation (k=1)", "ColQwen2 (colpali_engine), Ollama qwen2.5vl:7b"),
]


def svg_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def grouped_bar_chart(categories: list[str], series: dict[str, list[float | None]], colors: dict[str, str], y_max: float = 1.0, width: int = 820, height: int = 260) -> str:
    """Grouped bar chart as inline SVG. No JS; per-bar <title> gives a native hover tooltip."""
    margin_l, margin_r, margin_t, margin_b = 40, 10, 10, 30
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    n_cat = len(categories)
    n_series = len(series)
    band_w = plot_w / n_cat
    bar_w = band_w / (n_series + 1)

    def y_of(v: float) -> float:
        return margin_t + plot_h * (1 - v / y_max)

    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="grouped bar chart">']
    # gridlines + y labels
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = y_of(frac * y_max)
        parts.append(f'<line x1="{margin_l}" y1="{y:.1f}" x2="{width - margin_r}" y2="{y:.1f}" stroke="#262b36" stroke-width="1"/>')
        parts.append(f'<text x="{margin_l - 6}" y="{y + 3:.1f}" text-anchor="end" font-size="10" fill="#9aa4b2">{frac * y_max:.2f}</text>')
    # bars
    for ci, cat in enumerate(categories):
        band_x = margin_l + ci * band_w
        for si, (name, values) in enumerate(series.items()):
            v = values[ci]
            x = band_x + si * bar_w + bar_w * 0.15
            w = bar_w * 0.7
            if v is None:
                continue
            y = y_of(v)
            h = margin_t + plot_h - y
            color = colors.get(name, "#4f8ff7")
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}" rx="1.5">'
                f"<title>{svg_escape(name)}: {v:.2f}</title></rect>"
            )
        parts.append(f'<text x="{band_x + band_w / 2:.1f}" y="{height - 8}" text-anchor="middle" font-size="11" fill="#c7cdd6">{svg_escape(cat)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def legend(colors: dict[str, str], labels: dict[str, str]) -> str:
    items = []
    for key, color in colors.items():
        items.append(
            f'<span class="legend-item"><span class="swatch" style="background:{color}"></span>{svg_escape(labels.get(key, key))}</span>'
        )
    return '<div class="legend">' + "".join(items) + "</div>"


def metric_series(metric_key: str) -> tuple[list[str], dict[str, list[float | None]]]:
    categories, series = [], {col: [] for col in SUBSET_ORDER}
    for cid in CYCLE_ORDER:
        data = load_json(CYCLES[cid]["retrieval_file"])
        if data is None:
            continue
        categories.append(cid)
        for col in SUBSET_ORDER:
            series[col].append(data["metrics"].get(col, {}).get(metric_key))
    return categories, series


def failure_series(k: int) -> tuple[list[str], dict[str, list[float | None]]]:
    categories: list[str] = []
    series: dict[str, list[float | None]] = {"global": [], "single_hop": [], "multi_hop": [], "visual": []}
    metric_key = f"recall@{k}"
    for cid in CYCLE_ORDER:
        cfg = CYCLES[cid]
        data = load_json(cfg["retrieval_file"])
        if data is None:
            continue
        categories.append(cid)
        types = query_type_map(data)
        by_id = {d["id"]: d[metric_key] for d in data["details"]}

        def failure(ids: list[str]) -> float:
            return round(1 - sum(by_id[i] for i in ids) / len(ids), 4)

        all_ids = list(by_id.keys())
        series["global"].append(failure(all_ids))
        series["single_hop"].append(failure([i for i in all_ids if types[i] in SINGLE_HOP_TYPES]))
        series["multi_hop"].append(failure([i for i in all_ids if types[i] == "multi_hop"]))
        series["visual"].append(failure([i for i in all_ids if types[i] == "visual"]))
    return categories, series


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    thead = "".join(f"<th>{svg_escape(h)}</th>" for h in headers)
    tbody = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>'


def render_verdict_cards() -> str:
    cards = []
    for cid in ["-1", "1", "2", "3", "4", "5", "6", "7"]:
        meta = CYCLE_VERDICTS.get(cid)
        if meta is None:
            continue
        label, color = VERDICT_META[meta["verdict"]]
        cycle_label = CYCLES[cid]["label"] if cid in CYCLES else EXTRA_CYCLE_LABELS[cid]
        cards.append(
            f'<div class="card"><div class="card-head"><span class="cycle-id">Cycle {svg_escape(cid)}</span>'
            f'<span class="badge" style="background:{color}22;color:{color};border-color:{color}55">{svg_escape(label)}</span></div>'
            f'<div class="cycle-name">{svg_escape(cycle_label)}</div>'
            f'<p class="why">{svg_escape(meta["why"])}</p></div>'
        )
    return '<div class="card-grid">' + "".join(cards) + "</div>"


def render_bootstrap_table() -> str:
    rows = []
    for label, file_a, file_b, metric_key, subset in CORE_COMPARISONS:
        data_a, data_b = load_json(file_a), load_json(file_b)
        if data_a is None or data_b is None:
            continue
        types = query_type_map(data_a)
        ids = [i for i in types if subset == "global" or types[i] == subset]
        by_a = {d["id"]: d[metric_key] for d in data_a["details"]}
        by_b = {d["id"]: d[metric_key] for d in data_b["details"]}
        result = paired_bootstrap_delta([by_a[i] for i in ids], [by_b[i] for i in ids])
        note = "excludes 0" if result["excludes_zero"] else "includes 0"
        note_color = "#35c2a0" if result["excludes_zero"] else "#9aa4b2"
        rows.append([
            svg_escape(label), metric_key, subset.replace("_", "-"), str(result["n"]),
            f"{result['mean']:+.2f}", f"[{result['ci_low']:+.2f}, {result['ci_high']:+.2f}]",
            f'<span style="color:{note_color}">{note}</span>',
        ])
    return render_table(["Comparison", "Metric", "Subset", "n", "Δ mean", "95% CI", "CI vs. 0"], rows)


# Final synthesis (PLAN.md §5). Hand-authored: verdicts, costs and the
# "when it pays" column are interpretation, not a mechanical transform of any
# JSON. Keep in sync with the synthesis section in results.md.
SYNTHESIS_DECISIONS = [
    ("Dense retrieval (BGE-M3)", "Keep — the floor", "~106 min index build; 0.4–0.6s/query",
     "Always. Saturates semantic questions (R@5 1.00) and turns 0/18 post-cutoff facts into 13/18."),
    ("Hybrid (BM25 + RRF)", "Keep, conditionally", "~5s BM25 build; no query cost",
     "Only if you cannot afford a reranker. Buys exact-match (0.83→0.89) and multi-hop (0.42→0.50), costs semantic@5 (1.00→0.87). Net global delta: zero."),
    ("Cross-encoder reranking", "Keep — recommended stack", "0.38s → 29.6s/query on CPU; one 2.3 GB model",
     "Almost always. The only cycle whose bootstrap CI excludes zero on global recall@5 (+0.07) and MRR (+0.11)."),
    ("Hybrid <em>and</em> reranking", "Redundant", "both of the above",
     "Never, at this corpus size. dense+rerank ≡ hybrid+rerank on every metric (cycle-3 ablation). Drop the fusion, keep the reranker."),
    ("Contextual retrieval", "Drop", "~6h CPU context generation + ~100 min re-encode",
     "Not on this corpus. Zero measurable delta under the reranker; CI of the cycle 3→4 delta is a degenerate interval at 0.00."),
    ("Visual late interaction (ColQwen2)", "No verdict — closed", "~8.2h CPU index build",
     "Unknown. The run measured a model that loaded with a randomly initialized language backbone."),
    ("Agentic RAG (cycle 6)", "Declined on evidence", "–",
     "Trigger fired (multi-hop is the weakest non-visual subset) but its lever is retrieval, and past cycle 3 retrieval is not the binding constraint."),
    ("GraphRAG (cycle 7)", "Declined — no trigger", "–",
     "Global cross-corpus provenance questions never occur in the golden set."),
]


def ndcg_rerun_status() -> str:
    """One sentence about which cycles carry the fixed nDCG — derived, not asserted.

    Reading the provenance stamp instead of hard-coding the claim means the
    report can never say "all cycles were re-run" while an artifact on disk
    still carries the pre-fix numbers.
    """
    pending = [
        cid
        for cid in CYCLE_ORDER
        for data in [load_json(CYCLES[cid]["retrieval_file"])]
        if data is not None and data.get("eval_metrics_version") != CURRENT_METRICS_VERSION
    ]
    if not pending:
        return (
            "Every retrieval eval was re-run against the unchanged indexes, so all nDCG@10 "
            "values in <code>results.md</code> come from the fixed implementation; the "
            "before/after delta is printed there."
        )
    listed = ", ".join(pending)
    return (
        "Re-running every retrieval eval against the unchanged indexes is in progress: "
        f"cycle(s) <strong>{listed}</strong> still carry pre-fix nDCG@10 values and are marked "
        "with a warning sign in <code>results.md</code>'s nDCG table. No other metric is "
        "affected, and no re-indexing is involved — the re-runs only re-query existing indexes."
    )


def render_synthesis_section() -> str:
    rows = [[t, f"<strong>{v}</strong>", c, w] for t, v, c, w in SYNTHESIS_DECISIONS]
    table = render_table(["Technique", "Verdict", "What it costs", "When it pays"], rows)
    return f"""
  <section>
    <h2>The study&#39;s answer (read this first)</h2>
    <p>Six stacks, one corpus, one 59-query golden set, one new technique per cycle. The question was never &quot;can this be built&quot; but <strong>which technique earns its cost, for which question type, and by how much</strong>.</p>
    {table}
    <p><strong>1 &mdash; Hybrid search has a cost nobody quotes.</strong> BM25+RRF wins where the query carries distinctive tokens (a domain abbreviation, a literal number, a name) and loses where it does not: &quot;which club won&hellip;&quot; floods the top-10 with eighteen interchangeable table rows and pushes the answering row out. The semantic regression it causes was fully repaid by the reranker &mdash; after which the ablation showed the fusion had become dead weight.</p>
    <p><strong>2 &mdash; Contextual retrieval: six hours of compute for a delta of zero.</strong> A clean negative result, published rather than buried. Two caveats are owed to the technique: these chunks were never truly context-less, and the context generator was a 1.5B model.</p>
    <p><strong>3 &mdash; From cycle 3 on, the generator is the bottleneck, not retrieval.</strong> Retrieval kept improving (R@5 0.60&rarr;0.67, MRR 0.52&rarr;0.63) while end-to-end number-hit sat at 0.78 and the misses merely relocated between queries at temperature 0. That measurement, not fatigue, is why cycles 6 and 7 were declined.</p>
    <p class="meta">Full synthesis, including which findings should transfer to another corpus and which should not: see the closing section of <code>results.md</code>.</p>
  </section>
"""


def build_html(cycle5_section: str) -> str:
    recall5_cats, recall5_series = metric_series("recall@5")
    failure5_cats, failure5_series = failure_series(5)

    failure_labels = {**SUBSET_LABEL, "single_hop": "single-hop (semantic+exact-match)"}
    failure_colors = {"global": "#4f8ff7", "single_hop": "#35c2a0", "multi_hop": "#f2665e", "visual": "#b18cf5"}

    cost_rows = [[c, idx, lat, infra] for c, idx, lat, infra in COST_LATENCY]

    return f"""<title>scouting-rag — Retrieval Technique Comparison Study</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 2.5rem 1.25rem 5rem; background: #0b0e14; color: #e6e6e6;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.55;
  }}
  main {{ max-width: 920px; margin: 0 auto; }}
  h1 {{ font-size: 1.7rem; margin-bottom: 0.25rem; }}
  h2 {{ font-size: 1.2rem; margin-top: 3rem; border-bottom: 1px solid #262b36; padding-bottom: 0.5rem; }}
  .subtitle {{ color: #9aa4b2; margin-top: 0; }}
  .meta {{ color: #6b7280; font-size: 0.85rem; }}
  section p {{ color: #c7cdd6; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; margin: 0.75rem 0; }}
  th, td {{ text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #1c212b; }}
  th {{ color: #9aa4b2; font-weight: 600; white-space: nowrap; }}
  td {{ color: #dbe0e8; }}
  .card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.9rem; margin-top: 1rem; }}
  .card {{ background: #12151d; border: 1px solid #1c212b; border-radius: 10px; padding: 0.9rem 1rem; }}
  .card-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem; }}
  .cycle-id {{ font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; }}
  .cycle-name {{ font-weight: 600; margin-bottom: 0.4rem; }}
  .badge {{ font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 999px; border: 1px solid; white-space: nowrap; }}
  .why {{ font-size: 0.85rem; color: #9aa4b2; margin: 0; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 0.9rem; font-size: 0.8rem; color: #9aa4b2; margin: 0.4rem 0 0.8rem; }}
  .legend-item {{ display: inline-flex; align-items: center; gap: 0.35rem; }}
  .swatch {{ width: 10px; height: 10px; border-radius: 2px; display: inline-block; }}
  .chart-wrap {{ background: #12151d; border: 1px solid #1c212b; border-radius: 10px; padding: 0.9rem; }}
  .callout {{ background: #161a23; border-left: 3px solid #4f8ff7; padding: 0.7rem 1rem; border-radius: 6px; font-size: 0.88rem; color: #c7cdd6; }}
  .callout.warn {{ border-left-color: #f2b84b; }}
  a {{ color: #4f8ff7; }}
  footer {{ margin-top: 3rem; color: #6b7280; font-size: 0.8rem; }}
</style>
<main>
  <h1>scouting-rag: Retrieval Technique Comparison Study</h1>
  <p class="subtitle">A measured comparison of retrieval techniques (naive vector → hybrid → reranking → contextual → visual) over a mixed football-scouting corpus, entirely local and CPU-only.</p>
  <p class="meta">Generated by <code>scripts/render_report.py</code> from <code>eval/results/*.json</code> — regenerate after any eval change, never hand-edit.</p>

  <section>
    <h2>Verdicts at a glance</h2>
    {render_verdict_cards()}
  </section>

  {render_synthesis_section()}

  <section>
    <h2>Primary metric: Recall@5 per cycle</h2>
    <p>Judge-free retrieval metric against hand-annotated ground truth. Read text-cycle numbers against the effective ceiling (global 0.72, multi-hop 0.73 — visual ground truth is unreachable by design in text-only cycles).</p>
    {legend(SERIES_COLOR, SUBSET_LABEL)}
    <div class="chart-wrap">{grouped_bar_chart(recall5_cats, recall5_series, SERIES_COLOR)}</div>
  </section>

  <section>
    <h2>Retrieval failure rate (1 − Recall@5)</h2>
    <p>Same numbers, inverse framing (after Anthropic's Contextual Retrieval write-up): how often retrieval misses outright. Global failure drops 40%→33% from reranking; multi-hop failure (42%) resists it — the residual misses are structural, not a ranking problem.</p>
    {legend(failure_colors, failure_labels)}
    <div class="chart-wrap">{grouped_bar_chart(failure5_cats, failure5_series, failure_colors)}</div>
  </section>

  <section>
    <h2>Bootstrap confidence intervals (core comparisons)</h2>
    <p>Paired percentile bootstrap (10,000 resamples, fixed seed) over per-query values already in the eval JSONs — no new eval runs. "Excludes 0" is read as "deutet auf" (suggestive) at these sample sizes, not a classical significance claim.</p>
    {render_bootstrap_table()}
  </section>

  <section>
    <h2>Cost &amp; latency per cycle</h2>
    <p>Honest CPU numbers (no GPU), not production-representative.</p>
    {render_table(["Cycle", "Indexing (one-off)", "Latency / query", "Extra infra"], cost_rows)}
  </section>

  <section>
    <h2>Limitations (read before trusting any single number)</h2>
    <div class="callout warn">
      <strong>The golden set was written and annotated by the same AI that built the pipelines.</strong> <code>eval/SCHEMA.md</code> planned a 20% human review sample; the sample was generated (<code>eval/REVIEW_SAMPLE.md</code>) but the human review was never done. The honest figure is <em>zero percent independently reviewed</em> — query selection and ground-truth passages may carry the annotator's bias. The stats-based ground truth was extracted programmatically and is not affected.<br><br>
      <strong>Judge validation is thin — the faithfulness numbers are the softest in this report.</strong> The local judge (llama3.1:8b) is stable under test–retest (agreement 1.00, n=10) but agreed with a manual re-check on only <strong>7 of 13 cases strictly</strong> (10/13 under the honest-refusal reading), and that re-check was done by Claude, not a human. Known errors run in both directions: honest refusals scored unsupported, and answers that twisted the context scored supported. Treat "Faithful strict" / "Honest" as indicative aggregates only; the deterministic number-hit metric is the only judge-free answer-quality signal here, and it is what the cycle verdicts lean on.<br><br>
      <strong>Small samples.</strong> n = 13–18 per question type — one query can move a metric by 7–8 points. Every claim is "deutet auf", not "beweist".<br><br>
      <strong>A metric bug shipped, was visible for weeks, and is now fixed.</strong> nDCG@10 could exceed its 1.0 bound (cycle 4's semantic aggregate read 1.02) because DCG credited every rank that covered a ground-truth entry without deduplicating entries a higher rank had already covered. Fixed on 2026-09-20 in <code>eval_metrics.py</code> with three regression tests. {ndcg_rerun_status()} <em>Scope correction:</em> the earlier write-up claimed Precision@5 was "presumably similarly biased" — it was not. Precision@k is item-wise by definition and needs no ground-truth dedup; only DCG was ever affected, and recall@k and MRR never were.<br><br>
      <strong>One corpus, one language, one domain.</strong> 955k tokens of German football writing (72% from a single prose source) plus tables and self-rendered stat sheets. The finding least likely to transfer is "the fusion adds nothing once a reranker is present" — that is corpus-size dependent.<br><br>
      <strong>CPU-only latency.</strong> The reranker's 29.6s/query is honest for this machine and misleading for any machine with a GPU, where it is sub-second. Relative ordering transfers; absolute numbers do not.<br><br>
      <strong>Cycle 5 has no technique verdict.</strong> See below.
    </div>
  </section>

  {cycle5_section}

  <footer>scouting-rag · local, CPU-only, no paid APIs · see <code>results.md</code> for the full narrative and <code>PLAN.md</code> for the binding cycle plan.</footer>
</main>
"""


# Cycle-5 status: hand-authored (mirrors the results.md write-up), not
# derivable from any JSON since there is no cycle-5 eval run to read from.
# Update alongside results.md if the cycle-5 status changes.
CYCLE5_SECTION = """
  <section>
    <h2>Cycle 5: Visual retrieval (ColQwen2) — attempted, root-caused, closed</h2>
    <p>The intended showpiece: retrieve stat-sheet images directly via late interaction, no OCR, no chunking. It was built, the 84-page index was computed (~8.2h CPU at ~350s/page), and both the retrieval eval (59 queries) and the VLM generation (13 visual queries) actually ran. Every number in the tables above for cycle 5 comes from those runs.</p>
    <div class="callout warn">
      <strong>The result measured a broken model, not the technique.</strong>
      Recall@5 on the visual subset came out at 0.15 (2 of 13), 0 of 13 at rank 1.
      Inspecting the loaded state dict showed why: the ColQwen2 checkpoint
      (<code>vidore/colqwen2-v1.0</code>) loads with its language backbone's embedding and
      final-norm layers <strong>randomly initialized</strong> —
      <code>language_model.norm.weight</code> at exactly mean 1.0 / std 0.0 (untouched
      default init) and <code>embed_tokens.weight</code> at the textbook default std of
      0.0200, while the checkpoint's <code>model.*</code> keys are reported as unexpected.
      Worse, the same drift drops <strong>every LoRA weight of the retrieval fine-tune</strong>:
      14 tensor families across 28 layers (392 tensors) arrive as
      <code>MISSING</code> under <code>language_model.layers.*</code> while the checkpoint
      offers them as <code>model.layers.*</code>. Only <code>custom_text_proj</code> — the
      projection head outside the backbone — loads correctly, which is why nothing crashes.
      What ran was an untuned Qwen2-VL backbone with a random embedding table, not ColQwen2.
      That is a <code>colpali_engine==0.3.16</code> × <code>transformers==5.10.2</code>
      module-naming drift; pip's version ranges do not catch it because it is a runtime
      key-naming mismatch, not a range violation. Reproduced twice independently, inside
      and outside the eval harness. The corruption applies to the built index as well as to
      query-time embedding, so a fix requires a full re-index, not just a re-run.
      Full evidence &mdash; verbatim load reports, measured layer statistics, checkpoint key
      inspection &mdash; is committed in <code>docs/colqwen2-load-evidence.md</code>.
    </div>
    <p>A second, independent blocker: the intended <code>--k 5</code> generation run
    crashed immediately because <code>rag.py</code>'s <code>NUM_CTX=4096</code> was sized
    for text contexts and five images need ~7,900 prompt tokens. The reported end-to-end
    numbers are from an honest <code>--k 1</code> fallback, not from the designed setup.</p>
    <p><strong>Decision: closed at cycle 4.</strong> A fix path exists and is specified
    (a state-dict key-remapping shim at load time, avoiding a global <code>transformers</code>
    downgrade that would put the reranker and BGE-M3 at risk), and it was time-capped by the
    closing plan. The cap governed: cycle 5 is published as "attempted, root-caused to a
    reproducible tooling incompatibility, closed without a technique verdict", with the
    state-dict evidence committed. <strong>The 0.15 must not be read as "ColQwen2 is weak on
    football stat sheets."</strong> Publishing that would have been the easy and false
    version of this section.</p>
  </section>
"""


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    html = build_html(CYCLE5_SECTION)
    REPORT_PATH.write_text(html, encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
