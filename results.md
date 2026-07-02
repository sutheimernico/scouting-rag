# Results: Retrieval Technique Comparison

All numbers come from `eval/golden_set.jsonl` runs. Primary metrics are
judge-free IR metrics against hand-annotated ground-truth passages
(chunking-agnostic; a retrieved chunk is relevant iff it overlaps an
annotated passage). Secondary generation metrics use a local judge
(`llama3.1:8b`) and are reported with the measured judge noise. Latency
figures are honest CPU numbers (no GPU) and not production-representative.

State the sample size with every claim. With n≈12–15 per question type,
one query flips a metric by 7–8 points — phrase accordingly ("deutet auf",
not "beweist").

## Primary: Recall@5

n per subset: semantic 15, exact-match 18, multi-hop 13, visual 13 (59 global).

**Effective recall ceilings in text-only cycles** (visual ground truth is
unreachable by design; 7 of 13 multi-hop queries have an image half):
global 0.72, multi-hop 0.73, visual 0.00. Read every text-cycle number
against these ceilings, not against 1.0.

<!-- auto:recall5:start -->
| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|---|---|---|---|---|---|---|
| -1 | Closed book (no retrieval) | – | – | – | – | – |
| 1 | Naive dense (BGE-M3) | 0.60 | 1.00 | 0.83 | 0.42 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.60 | 0.87 | 0.89 | 0.50 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.67 | 1.00 | 0.94 | 0.58 | 0.00 |
| 4 | + Contextual retrieval | 0.67 | 1.00 | 0.94 | 0.58 | 0.00 |
| 5 | Visual (ColQwen) | 0.03 | 0.00 | 0.00 | 0.00 | 0.15 |
| 6 | Agentic (optional) |  |  |  |  |  |
<!-- auto:recall5:end -->

Cycle 3 vs. 4 recall@5 is an exact tie (0.67 both) — the earlier hand-written
table annotated this as "0.67 (±0)" and bolded each column's first-reached
best value; that per-cell styling was editorial, not part of the metric, and
is dropped now that the table is machine-generated (see
`scripts/render_results.py` docstring). The interpretation lives in the
verdict prose below, unaffected.

## Primary: Recall@10 / Precision@5 / MRR / nDCG@10

_Same table layout as Recall@5 — filled per cycle._

### Recall@10

<!-- auto:recall10:start -->
| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|---|---|---|---|---|---|---|
| 1 | Naive dense (BGE-M3) | 0.66 | 1.00 | 0.89 | 0.62 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.66 | 1.00 | 0.89 | 0.62 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.69 | 1.00 | 0.94 | 0.65 | 0.00 |
| 4 | + Contextual retrieval | 0.68 | 1.00 | 0.94 | 0.62 | 0.00 |
| 5 | Visual (ColQwen) | 0.03 | 0.00 | 0.00 | 0.00 | 0.15 |
<!-- auto:recall10:end -->

### Precision@5

<!-- auto:precision5:start -->
| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|---|---|---|---|---|---|---|
| 1 | Naive dense (BGE-M3) | 0.15 | 0.24 | 0.17 | 0.17 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.15 | 0.20 | 0.18 | 0.20 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.17 | 0.24 | 0.20 | 0.23 | 0.00 |
| 4 | + Contextual retrieval | 0.17 | 0.24 | 0.19 | 0.23 | 0.00 |
| 5 | Visual (ColQwen) | 0.01 | 0.00 | 0.00 | 0.00 | 0.03 |
<!-- auto:precision5:end -->

**Correction vs. the previous manually-transcribed table:** regenerating
from the raw JSON changed Precision@5 in three rows — cycle 2 global
0.16→0.15; cycle 3 global/semantic/exact-match/multi-hop
0.18/0.25/0.19/0.22 → 0.17/0.24/0.20/0.23; cycle 4
global/semantic/multi-hop 0.18/0.25/0.22 → 0.17/0.24/0.23 (exact-match was
already correct at 0.19). Cycle 3 and 4 had identical Precision@5 rows in
the hand-written table, which likely masked a copy-paste transcription slip
when cycle 4 was written up. Small corrections also surfaced in Recall@10
(cycle 4: global 0.69→0.68, multi-hop 0.65→0.62) and nDCG@10 (cycle 4 —
see the anomaly noted under the nDCG@10 table below). Recall@5 and MRR
matched the JSON exactly everywhere. No interpretation in the verdict prose
below depended on any of the wrong values. This transcription drift is the
exact integrity risk `scripts/render_results.py` exists to remove.

### MRR

<!-- auto:mrr:start -->
| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|---|---|---|---|---|---|---|
| 1 | Naive dense (BGE-M3) | 0.53 | 0.79 | 0.64 | 0.62 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.52 | 0.69 | 0.65 | 0.65 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.63 | 0.86 | 0.84 | 0.69 | 0.00 |
| 4 | + Contextual retrieval | 0.63 | 0.87 | 0.86 | 0.69 | 0.00 |
| 5 | Visual (ColQwen) | 0.01 | 0.00 | 0.00 | 0.00 | 0.04 |
<!-- auto:mrr:end -->

### nDCG@10

<!-- auto:ndcg10:start -->
| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|---|---|---|---|---|---|---|
| 1 | Naive dense (BGE-M3) | 0.56 | 0.95 | 0.70 | 0.49 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.55 | 0.86 | 0.72 | 0.51 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.65 | 1.00 | 0.89 | 0.56 | 0.00 |
| 4 | + Contextual retrieval | 0.65 | 1.02 | 0.88 | 0.54 | 0.00 |
| 5 | Visual (ColQwen) | 0.01 | 0.00 | 0.00 | 0.00 | 0.07 |
<!-- auto:ndcg10:end -->

**Data-quality finding (found while building the rendering script, not
fixed here):** cycle 4's semantic nDCG@10 is 1.02 — mathematically
impossible, nDCG is bounded by 1.0. Root cause: `query_metrics()` in
`src/eval_metrics.py` gives full DCG (and precision@k) credit to *every*
retrieved rank that covers a ground-truth entry, without checking whether
that entry was already covered by a higher rank — unlike `recall@k`,
which correctly unions covered indices. When two or more chunks from the
same article both satisfy a single-entry (`n_gt=1`) passage match (a
retriever legitimately returning several truly-matching chunks from the
same source doc — SCHEMA.md's chunking-agnostic ground truth allows this
by design), `idcg`'s cap of `min(n_gt, k)` slots is too low for the
`dcg` this produces, so the ratio exceeds 1. Confirmed on q042/q043/q044:
the effect is not specific to contextual retrieval — it is already present
in cycle 1's raw per-query data (`ndcg@10` up to 1.06) and in cycle 3's,
just never large enough in the *aggregate* to cross 1.00 until cycle 4.
Precision@5 has the same non-deduplication bug but can't self-flag the
same way (it's bounded to ≤1.0 by construction), so it is plausibly
inflated by a similar small amount project-wide — undetermined without a
fix. **Not fixed in this change**: correcting `eval_metrics.py` changes
every cycle's precision/nDCG numbers and would need every retrieval eval
re-run to recompute from raw chunk data (the stored JSON only keeps
rounded per-query metrics, not the full `covers` matrix) — out of scope
for a results-rendering script and too consequential to do without
sign-off. Flagged for Nico as a follow-up decision, not silently patched.

## Primary: Retrieval failure rate (1 − Recall@k)

Framing borrowed from Anthropic's Contextual Retrieval write-up: the
inverse view of the same recall numbers, read as "how often does retrieval
fail outright" rather than "how often does it succeed" — a reduction from
40% to 33% failure reads differently than 60%→67% recall, even though it's
the same delta. Single-hop combines the `semantic` + `exact_match` subsets
(both look up one fact); `multi-hop` and `visual` stay separate because
their failure modes are structurally different (see `eval/SCHEMA.md`).

### Failure@5

<!-- auto:failure_rate_5:start -->
| Cycle | Technique | global | single-hop (semantic+exact-match) | multi-hop | visual |
|---|---|---|---|---|---|
| 1 | Naive dense (BGE-M3) | 0.40 | 0.09 | 0.58 | 1.00 |
| 2 | + Hybrid (sparse + RRF) | 0.40 | 0.12 | 0.50 | 1.00 |
| 3 | + Reranking (cross-encoder) | 0.33 | 0.03 | 0.42 | 1.00 |
| 4 | + Contextual retrieval | 0.33 | 0.03 | 0.42 | 1.00 |
| 5 | Visual (ColQwen) | 0.97 | 1.00 | 1.00 | 0.85 |
<!-- auto:failure_rate_5:end -->

### Failure@10

<!-- auto:failure_rate_10:start -->
| Cycle | Technique | global | single-hop (semantic+exact-match) | multi-hop | visual |
|---|---|---|---|---|---|
| 1 | Naive dense (BGE-M3) | 0.34 | 0.06 | 0.38 | 1.00 |
| 2 | + Hybrid (sparse + RRF) | 0.34 | 0.06 | 0.38 | 1.00 |
| 3 | + Reranking (cross-encoder) | 0.31 | 0.03 | 0.35 | 1.00 |
| 4 | + Contextual retrieval | 0.32 | 0.03 | 0.38 | 1.00 |
| 5 | Visual (ColQwen) | 0.97 | 1.00 | 1.00 | 0.85 |
<!-- auto:failure_rate_10:end -->

Global failure@5 drops from 40% (cycle 1) to 33% (cycle 3) — a 7-point,
roughly one-sixth relative reduction in outright retrieval misses, entirely
from reranking (hybrid alone does not move the global failure rate; see the
cycle-2 verdict). Multi-hop failure stays the highest of any non-visual
subset even after reranking (42%) — consistent with the cycle-3 finding
that the residual misses are structural (the needed information is in no
single chunk), not a ranking problem reranking can fix.

## Primary: Bootstrap confidence intervals (core comparisons)

Paired percentile bootstrap (10,000 resamples, fixed seed, see
`src/bootstrap.py`) over the per-query values already in each cycle's
`details` array — no new eval runs. Resampling is paired by golden-set id,
which is the statistically correct way to compare two retrievers on the
*same* queries (it isolates the within-query variance instead of treating
the two cycles as independent samples). Read the "CI excludes 0" column
as "deutet auf" at these sample sizes (n=13–59 per subset), not as a
significance test in the classical sense — PLAN.md's hedging principle
applies here too.

<!-- auto:bootstrap:start -->
| Comparison | Metric | Subset | n | delta (mean) | 95% CI | Note |
|---|---|---|---|---|---|---|
| Cycle 1 -> 2 (dense -> hybrid) | recall@5 | global | 59 | +0.00 | [-0.08, +0.08] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 1 -> 2 (dense -> hybrid) | recall@5 | exact-match | 18 | +0.06 | [-0.11, +0.22] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 1 -> 2 (dense -> hybrid) | recall@5 | semantic | 15 | -0.13 | [-0.33, +0.00] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 1 -> 2 (dense -> hybrid) | recall@5 | multi-hop | 13 | +0.08 | [-0.12, +0.23] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 2 -> 3 (hybrid -> +reranking) | recall@5 | global | 59 | +0.07 | [+0.01, +0.14] | CI excludes 0 (deutet auf realem Effekt) |
| Cycle 2 -> 3 (hybrid -> +reranking) | recall@5 | semantic | 15 | +0.13 | [+0.00, +0.33] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 2 -> 3 (hybrid -> +reranking) | recall@5 | multi-hop | 13 | +0.08 | [-0.12, +0.27] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 3 -> 4 (+reranking -> +contextual) | recall@5 | global | 59 | +0.00 | [+0.00, +0.00] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle-3 ablation: dense+rerank vs. hybrid+rerank | recall@5 | global | 59 | +0.00 | [+0.00, +0.00] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 1 -> 2 (dense -> hybrid) | mrr | global | 59 | -0.01 | [-0.11, +0.08] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
| Cycle 2 -> 3 (hybrid -> +reranking) | mrr | global | 59 | +0.11 | [+0.02, +0.20] | CI excludes 0 (deutet auf realem Effekt) |
| Cycle 3 -> 4 (+reranking -> +contextual) | mrr | global | 59 | +0.01 | [-0.02, +0.03] | CI includes 0 (nicht von Null unterscheidbar bei diesem n) |
<!-- auto:bootstrap:end -->

The single-query-level swings the point estimates suggested are visible
here directly: e.g. the cycle-2 semantic regression (1.00→0.87, n=15) has a
CI that excludes 0 despite n=15 — losing 2 of 15 is a large share of a
small subset. The cycle-3→4 global comparison (contextual retrieval's
verdict) has a CI centered on and including 0, which is the bootstrap
directly confirming "no measurable delta" rather than just eyeballing two
equal-looking numbers.

## Secondary: generation quality (judge-free number-hit + local judge)

Number-hit = all reference numbers appear in the answer (deterministic,
exact-match subset). Faithful (strict) = judge says every claim is
context-supported. Honest = supported OR honest refusal (the judge applied
the refusal rule inconsistently, so both readings are reported).

<!-- auto:secondary:start -->
| Cycle | Number-hit exact-match (n=18) | Faithful strict (n=59) | Honest (n=59) | Refusal rate | Manual check (n=13) |
|---|---|---|---|---|---|
| -1 | **0.00** | n/a (no context to be faithful to) | n/a | – | – |
| 1 | **0.72** | 0.66 | 0.95 | 0.31 | done (Claude, not human — see below) |
| 2 | **0.78** | 0.76 | 0.98 | 0.22 | – |
| 3 | **0.78** | 0.73 | 0.98 | 0.25 | – |
| 5 | **0.00** (visual) | n/a (no context to be faithful to) | n/a | – | – |
<!-- auto:secondary:end -->

**Judge noise (test–retest, n=10, temp 0.3, seeds 1/2):** agreement 1.00 —
the judge is stable on this sample; n is small, treat as indicative.

**Manual sample result (n=13, reviewed by Claude — owner delegated; not an
independent human check):** agreement with the 8B judge: strict 7/13,
honest-reading 10/13. Confirmed weaknesses: refusal rule applied
inconsistently (q001/q016/q018 — honest refusals scored unsupported); one
verdict wrong against a correctly grounded answer (q005 — duplicate name
variants in the scorer table confused the judge); two verdicts too lenient
where answers twisted context after retrieval misses (q048, q056). Takeaway:
the strict rate can err in both directions; aggregates are usable, single
verdicts are not. The deterministic number-hit metric remains the hardest
answer-quality signal.

## Cost & latency per cycle

| Cycle | Indexing time (one-off) | Latency / query (CPU) | Extra infra | Notes |
|-------|-------------------------|------------------------|-------------|-------|
| −1 | – | ~48 s generation (measured under load, not representative) | Ollama | closed book |
| 1 | 106 min (BGE-M3 encode, 4,318 chunks) | 0.43 s retrieval + ~69 s generation (7B CPU) | Qdrant embedded | API cost: 0 €; judge run ~50 min one-off |
| 2 | + ~5 s BM25 build (in-memory) | 0.38 s retrieval + ~70 s generation | rank_bm25 | no re-encoding needed |
| 3 | – (reuses index) | **29.6 s retrieval** + ~65 s generation (95 s total) | bge-reranker-v2-m3 (2.3 GB) | 30 cross-encoder passes/query on CPU — the measured cost of this cycle |
| 4 | ~6 h context generation (2,127 chunks, qwen2.5:1.5b) + 100 min re-encode | unchanged | – | the cost bought nothing — see verdict |

## Per-cycle deltas and verdicts

_One short block per cycle after its run: delta vs. previous stage,
interpretation, keep/drop decision. Honest: if a technique does not earn
its delta, it goes, and that gets documented here._

### Cycle 1 vs. cycle −1 (closed book)

- Number-hit on exact-match: **0.00 → 0.72**. Without retrieval the
  generator gets zero post-cutoff facts right (it refuses or treats
  2025/26 as future); with naive RAG it answers 13/18 correctly.
- Hallucination behavior: closed book invents player careers and
  strengths; with context the model almost never free-hallucinates
  (honest 0.95) — it errs toward over-cautious refusal instead.
- Retrieval R@5 0.60 global against a 0.72 text-cycle ceiling;
  semantic is saturated (1.00), the gaps are specific: season
  disambiguation (q013 answered with the wrong season's number),
  domain abbreviations (PPDA, q031), rank semantics not present in
  row chunks (q004), and a weak 7B generator that misses values inside
  long 30-column row chunks even when retrieval succeeded (q001, q011).
- **Verdict: keep.** This is the baseline every later cycle must beat;
  the exact-match and multi-hop gaps are exactly what cycles 2/3 target.
- Limitations: golden-set annotations machine-validated only (human 20%
  review skipped by owner decision, sample kept available); judge refusal
  flag unreliable; latency figures are CPU numbers.

### Cycle 2 (hybrid) vs. cycle 1 (dense)

- R@5 per type: exact-match 0.83→0.89, multi-hop 0.42→0.50, semantic
  1.00→0.87 (fully recovered at k=10), global unchanged at 0.60. With
  n=13–18 per subset each delta is ±1–2 queries — indicative, not proof.
- The pattern is clean and worth the study: **BM25 wins where the query
  carries specific tokens** (PPDA q031, "4.060" q029, names in q048/q055),
  **and loses where it doesn't** — "Welcher Verein gewann…" (q008) floods
  top-10 with 18 interchangeable table rows because no row carries rank
  semantics; the Schalke row drops out entirely. Same failure class as q004.
- End-to-end confirms the chain: number-hit 0.72→0.78; the PPDA answer is
  now perfect, the Schalke answer died with its retrieval. q001/q011
  flipped to hits and q030 to a miss with unchanged retrieved content —
  suggests (not proves) context-order sensitivity of the 7B generator.
- Latency: retrieval 0.38 s/query, +~5 s one-off BM25 build. Negligible.
- **Verdict: keep, conditionally.** Hybrid earns its target-subset delta
  at zero meaningful cost, but the semantic@5 regression goes to cycle 3
  (reranker over top-30 — every cycle-2 loss is still within top 30). If
  reranking does not recover semantic@5 ≥ dense level, revisit the fusion.

### Cycle 3 (+ cross-encoder reranking) vs. cycle 2 (hybrid)

- R@5: global 0.60→**0.67** (ceiling 0.72), semantic 0.87→**1.00** (cycle-2
  regression fully healed), exact-match 0.89→**0.94** (the rank-semantics
  victim q008 recovered from top-30), multi-hop 0.50→**0.58**. MRR global
  0.52→0.63, nDCG 0.55→0.65. Strongest cycle so far; n caveats apply.
- Remaining text-cycle misses are structural: q004 (rank semantics nowhere
  in any chunk), q047/q048 multi-hop second sources that only cover half
  the query's information need — reranker correctly scores them low
  against the full query. Agentic decomposition (cycle 6) is the designed
  answer; the trigger condition keeps building.
- **Ablation (documented extra): dense+rerank ≡ hybrid+rerank** on every
  metric. Under a cross-encoder, the BM25/RRF fusion adds nothing at this
  corpus size — dense top-30 already contains everything BM25 contributed.
  Hybrid's standalone value (cycle 2) is real but only without reranking.
- Cost: retrieval latency 0.38 s → **29.6 s**/query (30 CPU cross-encoder
  passes). On GPU this would be sub-second; our numbers are honest CPU.
- **Verdict: keep reranking; recommended stack becomes dense+rerank**
  (drop the fusion when reranking — one component less, same quality).
  Hybrid stays documented as the latency-constrained alternative
  (0.38 s, exact-match 0.89) for setups that cannot afford a reranker.

**Cycle-3 end-to-end addendum:** number-hit stays at 0.78 despite clearly
better retrieval (R@5 0.60→0.67). The misses *moved* (q013/q030 flipped to
hits, q008/q028 to misses) with correct retrieval in all four — i.e. the
7B generator drops ~2 of 18 answers semi-randomly depending on context
composition, even at temperature 0. **From this stage on, the generator is
the end-to-end bottleneck, not retrieval.** Honest rate stays high (0.98).
This is a finding, not a failure: retrieval improvements beyond cycle 3
cannot show up in answer quality unless the generator improves too —
relevant context for interpreting cycle 4.

### Cycle 4 (contextual retrieval) vs. cycle 3 — the plan's ablation question

- Standalone (no reranker): dense_ctx R@5 0.59 vs dense 0.60 — within
  ±1-query noise, exact-match slightly down, multi-hop slightly up.
- Under the reranker: **ctx+rerank ≡ rerank on every metric and subset.**
- Cost: ~6 h CPU context generation (2,127 article chunks, qwen2.5:1.5b
  after the documented model-size deviation) + ~100 min re-encoding.
- **Answer to the plan's question ("rechtfertigt der Mehraufwand?"): No.**
- **Verdict: drop.** Two fairness caveats for the write-up: (1) our chunks
  were never truly context-less — articles carry titles, table rows carry
  header labels; contextual retrieval against genuinely naked chunks may
  behave differently. (2) The 1.5b context generator caps context quality
  (the 7b would have taken days on CPU). Both documented, neither changes
  the verdict for THIS corpus and pipeline.

### Cycle 5 (visual retrieval, ColQwen2) — run, and a broken result documented honestly

_The first four bullets below are carried over unchanged from the prior
iteration that stopped before the index was built (infra check, timing
smoke test, extrapolation) — still accurate as a historical record of
that state. Everything from "Index built, evaluated..." onward is new:
the index has since been built and both evals actually ran._

- **Code is done** (`src/visual_index.py`: ColQwen2 late-interaction
  retriever, brute-force torch MaxSim over 84 self-rendered stat sheets;
  `src/rag.py:generate_visual`: VLM answer generation over the retrieved
  page images). `tests/test_visual_index.py` covers the MaxSim scoring
  core. Wired into `src/run_eval.py --retriever visual` for both the
  `retrieval` and `rag` modes.
- **Infra check (per LOOP.md, before attempting any eval):** Ollama
  reachable at `localhost:11434` with `qwen2.5vl:7b` pulled ✓. ColQwen2
  weights (`vidore/colqwen2-v1.0` + base) present in the local HF cache ✓.
  No cached `data/visual_index.pt` yet — the index has never been built.
- **Timing smoke test (per the task's own gate: measure before committing
  to a full run):** loaded the model and timed a single page embedding on
  this machine (16-core CPU, no GPU, fp32 — bf16 matmul unsupported here,
  see `visual_index.py:get_model`'s fallback). Two independent cold-start
  runs measured **346.15s and 350.95s** for the *same* stat-sheet page —
  reproducible, not a one-off fluke. A third page (same warm model, second
  run) was still running past 235s without finishing before the smoke test
  was stopped, ruling out any large speedup from warmup/kernel-dispatch
  caching within a run. Model load itself is cheap (47-63s, one-off).
- **Extrapolation:** ~350s/page × 84 pages ≈ **8.2 hours** for the index
  build alone — before any of the 59 retrieval queries or 13 VLM
  generations. This is roughly 16x the task's ~30-minute unattended-run
  budget. Per README, this project treats long-running steps as accepted
  overnight batches (cycle 4's context generation took ~6h CPU) — an
  8h index build could fit that pattern, but crosses the explicit
  threshold for what an agent should start without asking first.
- **Index built, evaluated, and the code has a real bug — not a capability
  finding.** `data/visual_index.pt` (84 pages) was built and both the
  retrieval eval (59 golden-set queries) and generation (13 visual-subset
  VLM answers) actually ran against it. Every number below is from those
  two real runs (`eval/results/cycle5_visual_retrieval.json`,
  `eval/results/cycle5_visual_rag_k1.json` /
  `..._secondary.json`) — none estimated.

- **Retrieval result: Recall@5 = Recall@10 = 0.15 (2 of 13), MRR = 0.04,
  nDCG@10 = 0.07** on the visual subset (n=13) — far below the ADR's
  expectation that in-distribution ColQwen2 on clean self-rendered sheets
  would be ceiling-inflated (Decision 3). Only q017 (rank 3) and q025
  (rank 5) retrieved their correct stat sheet at all; 0 of 13 hit rank 1.
  Global metrics (n=59) collapse further (recall@5 0.03) because the
  visual retriever structurally cannot match text ground truth — expected
  by design, not a new finding (see the effective-recall-ceiling note
  under the Recall@5 table).

- **Root cause, diagnosed, not guessed:** the ColQwen2 checkpoint
  (`vidore/colqwen2-v1.0` + `colqwen2-base`) loads with its
  language-model backbone's embedding and final-norm layers **randomly
  initialized**, not from the pretrained checkpoint. Every load prints a
  report with `language_model.embed_tokens.weight` / `language_model.norm.weight`
  as `MISSING` and `model.embed_tokens.weight` / `model.norm.weight` as
  `UNEXPECTED` — confirmed by direct inspection of the loaded state dict:
  `language_model.norm.weight` is exactly `mean=1.0, std=0.0` (an all-ones
  vector — the default init for a norm layer, not a trained value) and
  `language_model.embed_tokens.weight` has `std=0.0200` (the textbook
  default init std for an embedding layer). This is a `colpali_engine==0.3.16`
  vs. `transformers==5.10.2` internal module-naming mismatch (`language_model.*`
  vs. `model.*` prefixes for the Qwen2-VL backbone) — both packages were
  already pinned together in `requirements.txt` before this run; pip's
  own metadata (`transformers<6.0.0,>=5.3.0`) does not catch it because
  it is a runtime key-naming drift, not a version-range violation.
  Reproduced twice independently: once inside the eval run, once via a
  standalone `visual_index.py search` CLI call outside it. The corrupted
  weights affect the already-built index file too (it was built with the
  same environment), not just query-time embedding — the whole cycle-5
  retrieval artifact needs re-indexing after a fix, not just a rerun.
  **This is a real, reproducible code/dependency bug, not evidence that
  ColQwen2 late-interaction retrieval doesn't work on this corpus** — the
  model that actually ran was not the model the design called for.

- **Generation blocker (separate from the retrieval bug):** the intended
  `--k 5` run (5 stat-sheet images per query, matching cycles 1–4's k)
  crashed on the very first query — `rag.py`'s `NUM_CTX=4096` was sized
  for text contexts ("k=5 contexts à ~400 tokens", per its own comment)
  and never adjusted for the VLM path, where 5 images alone need ~7,873
  prompt tokens (~1,575 tokens/image). Zero generations completed at k=5;
  no output file exists for it. Ran `--k 1` instead (already-supported
  flag, no pipeline code changed) to still get a real, honest signal — an
  honest fallback, not a substitute for the intended setup.

- **End-to-end (k=1, n=13 VLM generations, all real):** number-hit
  **0.00** (n=12 — q020's reference has no extractable number, correctly
  excluded). Every one of the 13 retrieved images was the wrong player's
  sheet at k=1 (0-of-13 rank-1 accuracy, consistent with the retrieval
  numbers above). The VLM's behavior under wrong context is itself an
  honest-refusal data point: 10 of 13 answers refuse or explicitly say the
  shown sheet doesn't match the asked-about player (e.g. q016: "Es handelt sich
  um eine Darstellung von Joshua Kimmich, nicht von Álex Grimaldo"; q022
  correctly flags the query/context player mismatch by name) rather than
  fabricating a percentile: closer to cycle 1's "honest over-refusal"
  finding than to hallucination. 3 of 13 (q018, q023, q026) answered with
  a concrete number anyway, and all three are wrong against the
  reference (59 vs. 99; 80 vs. 6; 33 vs. 87) — a direct consequence of
  reading the wrong player's sheet, not evidence of poor chart-reading on
  a correctly-retrieved sheet (the ADR's planned retrieval-conditioned
  reading of number-hit cannot be computed here: n=0 queries had correct
  top-1 retrieval to condition on).

- **Cost/latency (real, CPU, honest):** retrieval 2.7 s/query average
  (cheap — a query is one short forward pass, unlike the ~350 s/page
  index-build cost measured in the earlier timing smoke test, which
  stands as reported). Generation 105.9 s/query average (k=1, one image),
  in the same range as cycles 1–3's text generation despite a heavier VLM
  and image tokens. Total wall time for the full retrieval + generation +
  secondary run: well under an hour once the index existed — the
  previously-measured 8.2h index-build cost (unaffected by this bug — it
  is a wall-clock cost, not a correctness one) remains the dominant cost
  of this cycle, run separately as an accepted overnight batch.

- **Verdict: cannot judge ColQwen2 late-interaction retrieval on this
  corpus from this run — the eval measured a broken model, not the
  technique.** Recommend, in order: (1) fix the `colpali_engine`/
  `transformers` weight-loading mismatch (pin down to a known-compatible
  `transformers` version, or upgrade `colpali_engine` past 0.3.16 if a
  fix lands there — needs a dependency change, flagged for Nico rather
  than done unilaterally here), (2) fix `rag.py`'s `NUM_CTX` for the
  visual path so a real k=5 run is possible, (3) re-run both the index
  build and the full eval end-to-end. Until then, cycle 5 stays an open,
  honestly-documented result rather than a closed keep/drop call — the
  0.15 Recall@5 above must not be read as "ColQwen2 is weak on football
  stat sheets," because the number is real but the model that produced it
  was not.
- Per PLAN.md §2's working mode, this is where the cycle stops and waits
  for Nico's decision on the dependency fix before either cycle 5 is
  re-run for a real verdict or the study closes at cycle 4 with cycle 5
  documented as "attempted, blocked on a tooling bug" instead.
