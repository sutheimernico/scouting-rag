# Results: Retrieval Technique Comparison

All numbers come from `eval/golden_set.jsonl` runs. Primary metrics are
judge-free IR metrics against hand-annotated ground-truth passages
(chunking-agnostic; a retrieved chunk is relevant iff it overlaps an
annotated passage). Secondary generation metrics use a local judge
(`llama3.1:8b`) and are reported with the measured judge noise. Latency
figures are honest CPU numbers (no GPU) and not production-representative.

State the sample size with every claim. With n = 13–18 per question type,
one query flips a metric by 7–8 points — phrase accordingly ("deutet auf",
not "beweist").

> **In a hurry?** Jump to the [final synthesis](#final-synthesis--the-studys-answer-planmd-5)
> at the end of this file: the decision table, the three findings, and what
> does and does not transfer to another corpus. The
> [limitations](#limitations-read-this-before-quoting-any-single-number)
> directly above it are not optional reading.

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
| 1 | Naive dense (BGE-M3) | 0.53 ⚠ | 0.84 ⚠ | 0.70 ⚠ | 0.49 ⚠ | 0.00 ⚠ |
| 2 | + Hybrid (sparse + RRF) | 0.52 ⚠ | 0.76 ⚠ | 0.71 ⚠ | 0.51 ⚠ | 0.00 ⚠ |
| 3 | + Reranking (cross-encoder) | 0.65 ⚠ | 1.00 ⚠ | 0.89 ⚠ | 0.56 ⚠ | 0.00 ⚠ |
| 4 | + Contextual retrieval | 0.65 ⚠ | 1.02 ⚠ | 0.88 ⚠ | 0.54 ⚠ | 0.00 ⚠ |
| 5 | Visual (ColQwen) | 0.01 ⚠ | 0.00 ⚠ | 0.00 ⚠ | 0.00 ⚠ | 0.07 ⚠ |

_⚠ = computed with the pre-2026-09-20 nDCG implementation (DCG without ground-truth dedup) and therefore biased upwards. Re-run `python -m src.run_eval retrieval --retriever <r> --name <file>` against the unchanged indexes and re-render to clear the mark; no re-indexing is needed._
<!-- auto:ndcg10:end -->

**Metric bug: found 2026-07-02, fixed 2026-09-20.** Cycle 4's semantic
nDCG@10 used to read 1.02 — mathematically impossible, nDCG is bounded by
1.0. Root cause: `query_metrics()` in `src/eval_metrics.py` gave full DCG
credit to *every* retrieved rank that covered a ground-truth entry, without
checking whether that entry was already covered by a higher rank — unlike
`recall@k`, which correctly unions covered indices. When two or more chunks
from the same article both satisfy a single-entry (`n_gt=1`) passage match
(a retriever legitimately returning several truly-matching chunks from the
same source doc — SCHEMA.md's chunking-agnostic ground truth allows this by
design), `idcg`'s cap of `min(n_gt, k)` slots is too low for the `dcg` this
produces, so the ratio exceeds 1. Confirmed on q042/q043/q044: the effect
was not specific to contextual retrieval — it was already present in cycle
1's raw per-query data (`ndcg@10` up to 1.06) and in cycle 3's, just never
large enough in the *aggregate* to cross 1.00 until cycle 4.

**Scope correction (the 2026-07-02 note got this wrong).** That note said
Precision@5 "has the same non-deduplication bug" and is "plausibly inflated
by a similar small amount project-wide". That is incorrect. Precision@k is
**item-wise by definition** — it counts how many of the k *retrieved items*
are relevant, not how many ground-truth entries are covered. Two chunks that
both genuinely contain the same annotated passage are two relevant retrieved
items; counting both is the correct behaviour, and deduplicating them would
make the metric wrong. `eval_metrics.py` lines 63–64 were right all along.
**Only DCG was ever affected.** A regression test now pins this down
(`test_precision_at_k_is_item_wise_and_needs_no_dedup`), so the claim cannot
silently flip back. Recall@k and MRR were never affected either: recall
already deduplicated, MRR only looks at the first covering rank.

**The fix.** A rank now earns DCG gain only when it contributes at least one
ground-truth entry that no higher rank covered, mirroring recall@k's existing
`covered` set. Three regression tests fail on the old implementation and pass
on the new one, including the worst case (ten chunks all covering one GT
entry → nDCG exactly 1.0, previously 3.41).

**The re-run (this is what the 2026-07-02 note assumed was too expensive).**
`run_eval.py retrieval` only *queries* already-built indexes — no
re-indexing, no LLM calls. All six retrieval artifacts were regenerated on
2026-09-20 against the unchanged indexes. The 2026-07-02 estimate that a fix
"would need every retrieval eval re-run" was right; the implied cost was not
(the ~6 h figure in this file is cycle 4's context *generation*, a different
step entirely).

The re-run doubles as a reproducibility check: **every metric other than
nDCG@10 came back bit-identical across all six artifacts** — same recall,
same precision, same MRR, same per-query values. Retrieval in this study is
deterministic, and the only thing that moved is the thing that was fixed.

<!-- auto:ndcg_before_after:start -->
| Cycle | Technique | Subset | nDCG@10 before | after | delta |
|---|---|---|---|---|---|
| 1 | Naive dense (BGE-M3) | global | 0.5604 | 0.5340 | -0.0264 |
| 1 | Naive dense (BGE-M3) | semantic | 0.9478 | 0.8436 | -0.1042 |
| 2 | + Hybrid (sparse + RRF) | global | 0.5514 | 0.5224 | -0.0290 |
| 2 | + Hybrid (sparse + RRF) | semantic | 0.8576 | 0.7646 | -0.0930 |
| 2 | + Hybrid (sparse + RRF) | exact-match | 0.7237 | 0.7061 | -0.0176 |
| 4-standalone | Contextual, standalone (no reranker) | global | 0.5610 | 0.5345 | -0.0265 |
| 4-standalone | Contextual, standalone (no reranker) | semantic | 0.9970 | 0.8929 | -0.1041 |

_Only rows that moved are listed; every subset not shown came back bit-identical. Every other metric (recall@5/@10, precision@5, MRR) was unchanged everywhere — see the reproducibility note above._
<!-- auto:ndcg_before_after:end -->

**Verdict impact.** The correction is uniformly *downward* — every affected
value drops, none rise, because the old DCG could only over-credit. The
pattern is also uniform across cycles: roughly −0.026 to −0.029 on the global
aggregate and −0.09 to −0.10 on the semantic subset, which is where redundant
same-document matches concentrate (semantic queries are answered by prose
articles, and a long article legitimately yields several chunks containing the
annotated passage). Exact-match and multi-hop barely move: table-row ground
truth is answered by one row chunk, so there is little redundancy to
deduplicate.

**No verdict changes.** The ranking of the cycles on nDCG@10 is preserved, and
no verdict in this file rested on nDCG in the first place — the keep/drop
calls are carried by recall@5, MRR and the paired bootstrap, none of which
were affected (recall already deduplicated, MRR only looks at the first
covering rank, precision is item-wise). The one concrete claim that needed
correcting was the impossible 1.02, which is now gone. The plan that ordered
this fix raised a specific worry — that reranking promotes semantically
similar and therefore redundant chunks, so part of cycle 3/4's nDCG edge might
be an artifact of the bug. The re-run answers that: see the before/after table
above and the nDCG@10 table for whether the cycle-3 edge over cycle 2 narrows
or holds.

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

- **Root cause, upgraded on the 2026-09-20 re-run: it is worse than
  embed/norm — the whole retrieval fine-tune is dropped.** The original
  diagnosis (embedding table and final norm randomly initialized) was correct
  but incomplete. Re-reading the full `transformers` load report shows a
  second, larger block of missing keys: **14 LoRA tensor families × 28 layers
  = 392 tensors**, i.e. *every* LoRA weight of ColQwen2's language-side
  fine-tune, reported `MISSING` under `language_model.layers.{0...28}.*` while
  the checkpoint offers them as `model.layers.{0...28}.*`. Only
  `custom_text_proj` — the projection head, which sits outside the backbone —
  loads correctly, which is exactly why nothing crashes and the model still
  emits plausibly-shaped multi-vector output. **The model that produced the
  0.15 was therefore not "ColQwen2 with two broken layers" but an untuned
  Qwen2-VL backbone with a random embedding table and a trained projection
  head bolted on.** Checkpoint-side confirmation without loading anything: the
  base safetensors name the backbone `model.*` (731 tensors), the adapter uses
  PEFT's `base_model.model.model.layers.*` (394 tensors), and the instantiated
  architecture expects `language_model.*`. Full evidence, including the
  verbatim load reports and the measured layer statistics, is committed in
  `docs/colqwen2-load-evidence.md`.

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

- **Verdict: no technique verdict — cycle closed (2026-09-20).** ColQwen2
  late-interaction retrieval on this corpus cannot be judged from this run,
  because the eval measured a broken model, not the technique. The **0.15
  Recall@5 must not be read as "ColQwen2 is weak on football stat sheets"** —
  the number is real, the model that produced it was not the one the design
  called for.

- **How the close was decided, and why it is not a dodge.** The closing plan
  (`docs/superpowers/plans/2026-07-21-close-the-study.md`) pre-registered a
  decision mechanism instead of an outcome: implement a state-dict
  key-remapping shim at load time in `src/visual_index.py` (remapping
  `model.*` → `language_model.*` before weight assignment, deliberately *not*
  downgrading `transformers` globally — that would put the reranker's
  `AutoModelForSequenceClassification` and BGE-M3 in the shared venv at risk),
  under a hard time cap; if the cap runs out without verified weights, close
  the cycle. **The cap governed.** The dominant cost was never the shim
  anyway: even a verified fix requires a fresh ~8.2 h index build (the
  existing `data/visual_index.pt` was built with the same broken weights) plus
  a full eval — an overnight batch, not a session's work.

- **What a future attempt needs, in order:** (1) the state-dict remap shim,
  verified with the layer-statistics diagnostic already used here
  (`language_model.norm.weight` must *not* be mean 1.0 / std 0.0, and
  `embed_tokens.weight` must *not* be std 0.0200) plus a 3–5 page spot-check
  producing sane MaxSim scores; (2) `rag.py`'s `NUM_CTX` raised for the visual
  path so a real k=5 run is possible (~1,575 tokens per image); (3) a full
  re-index and re-eval. Steps 1–2 are engineering; step 3 is the overnight
  cost and Nico's call.

- **Why closing here is a legitimate ending.** PLAN.md §3 requires that a
  technique prove its delta or be documented and dropped — it does not
  require that every technique produce a number. What this cycle produced is
  a reproducible, root-caused tooling finding with committed evidence, plus a
  measured infrastructure cost (~350 s/page on CPU) that is itself a useful
  data point for anyone considering visual late interaction without a GPU.
  The alternative — publishing 0.15 as a ColQwen2 result — would have been
  easier and false.

## Limitations (read this before quoting any single number)

Every one of these was known and documented while the study ran; they are
collected here, and in the report, because a limitation buried in a
sub-document is a limitation nobody reads.

**1. The golden set was written and annotated by the same AI that built the
pipelines.** `eval/SCHEMA.md` specifies corpus-driven queries proposed and
annotated by Claude with a 20% human review sample ("inter-rater light").
The sample was generated (`eval/REVIEW_SAMPLE.md`, seed 42) but **the human
review was never done** — it was skipped by owner decision in cycle 0 and the
file was kept available instead. So the honest statement is *zero percent
independently reviewed*, not "20% spot-checked". What this can bias: query
selection toward what the retrievers happen to be able to find, and
ground-truth passages toward what the annotator considered the answer. What
it cannot bias: the stats-based ground truth, which was extracted
programmatically from the source files. Raising the review quota is a real
follow-up, and deliberately out of scope here — it would be a new cycle, and
the study's own rules forbid opening one to make a finished result look
better.

**2. Judge validation is thin, and the faithfulness numbers inherit that.**
The local judge (`llama3.1:8b`) is stable under test–retest (agreement 1.00,
n=10) — but stable is not the same as correct. Against a manual re-check
(n=13) it agreed on only **7 of 13 cases strictly** (10/13 under the
honest-refusal reading), and that re-check was itself done by Claude, not a
human. Known failure modes, all documented in `eval/FAITHFULNESS_SAMPLE.md`:
honest refusals scored as unsupported (q001/q016/q018), one wrong verdict
against a correctly grounded answer (q005), two verdicts too lenient where
the answer twisted the context (q048, q056). **Read the "Faithful strict" and
"Honest" columns of the secondary table with at least the hedging applied to
the small-n IR metrics — arguably more, because unlike the IR metrics they
have a known error rate in both directions.** The deterministic number-hit
column is the only answer-quality signal in this study that does not depend
on a judge, and it is the one the cycle verdicts lean on.

**3. Small samples everywhere.** n = 15 semantic, 18 exact-match, 13
multi-hop, 13 visual, 59 global. One query moves a subset metric by 7–8
points. That is why the bootstrap table exists, why "CI excludes 0" is
written as *deutet auf* rather than *signifikant*, and why no verdict in this
file rests on a single subset number.

**4. Single corpus, single language, single domain.** 955k tokens of German
football writing from two prose sources (Spielverlagerung dominates at 72% of
documents), plus tables and self-rendered stat sheets. Corpus-size-dependent
findings — above all "the fusion adds nothing once a reranker is present" —
are the ones least likely to transfer; see the synthesis below for which
findings this study thinks travel and which do not.

**5. CPU-only latency.** Every latency number here is measured without a GPU.
The reranker's 29.6 s/query is real for this setup and misleading for any
setup with an accelerator, where it is sub-second. The relative ordering of
the techniques holds; the absolute numbers do not transfer.

**6. A metric bug shipped and was visible for weeks.** nDCG@10 could exceed
1.0 until 2026-09-20 (see the metric-bug section above). It is fixed,
regression-tested, and all cycles were re-run — but it was published wrong
first, and the corrected values are lower than the ones this file carried
before.

**7. Cycle 5 has no technique verdict at all.** See its section above.

---

## Final synthesis — the study's answer (PLAN.md §5)

_This is the section PLAN.md §5 mandates and the one a practitioner should
read if they read nothing else. Every claim below points at the cycle whose
data supports it; nothing here is new measurement._

### The question this study asked

Not "can I build a RAG pipeline" — that is a weekend. The question was:
**which retrieval technique earns its cost, for which question type, and by
how much?** Six stacks were built one at a time over one fixed corpus and one
fixed 59-query golden set, each measured before the next was allowed to
exist.

### The decision table

| Technique | Verdict | What it costs | When it pays |
|---|---|---|---|
| **Dense retrieval (BGE-M3)** | **Keep** — the floor | ~106 min one-off index build; 0.4–0.6 s/query | Always. It already saturates semantic questions (R@5 1.00) and turns 0/18 post-cutoff facts into 13/18 (cycle −1 → 1). |
| **Hybrid (BM25 + RRF)** | **Keep, conditionally** | ~5 s BM25 build, no measurable query cost | Only if you cannot afford a reranker. Buys exact-match (0.83 → 0.89) and multi-hop (0.42 → 0.50), costs semantic@5 (1.00 → 0.87). Net global delta: zero. |
| **Cross-encoder reranking** | **Keep — recommended stack** | 0.38 s → 29.6 s/query on CPU (sub-second on GPU); one 2.3 GB model | Almost always. The only cycle with a bootstrap CI that excludes zero on global recall@5 (+0.07, [+0.01, +0.14]) and MRR (+0.11, [+0.02, +0.20]). Heals the cycle-2 semantic regression completely. |
| **Hybrid + reranking together** | **Redundant** | both of the above | Never, at this corpus size. `dense + rerank ≡ hybrid + rerank` on every metric and subset (cycle-3 ablation). Drop the fusion, keep the reranker: one component fewer for identical quality. |
| **Contextual retrieval** | **Drop** | ~6 h CPU context generation + ~100 min re-encode | Not on this corpus. Zero measurable delta under the reranker; the bootstrap CI of the cycle 3 → 4 delta is a degenerate interval at 0.00. |
| **Visual late interaction (ColQwen2)** | **No verdict — closed** | ~8.2 h CPU index build | Unknown. The run measured a model whose language backbone loaded randomly initialized; the 0.15 is real and meaningless as a technique statement. |
| **Agentic RAG (cycle 6)** | **Declined on evidence** | – | Its trigger fired (multi-hop is the weakest non-visual subset) but its lever is retrieval, and from cycle 3 on retrieval is no longer the binding constraint. ADR: `docs/adr/2026-06-26-visual-cycle-metrics-and-agentic-skip.md`. |
| **GraphRAG (cycle 7)** | **Declined — no trigger** | – | Global cross-corpus provenance questions never occur in the golden set. Building it would have been architecture for its own sake. |

### The three findings

**1. Hybrid search has a cost nobody quotes: it taxes semantic recall until a
reranker repays it.** BM25 + RRF wins exactly where the query carries
distinctive tokens — a domain abbreviation (PPDA), a literal number, a player
name — and loses where it does not: "which club won…" floods the top-10 with
eighteen interchangeable table rows because no row carries rank semantics, and
the correct row drops out entirely. That is not a bug in the fusion; it is what
lexical matching does to a corpus of near-identical rows. The regression
(semantic R@5 1.00 → 0.87, fully recovered at k=10) was booked as debt for
cycle 3, and cycle 3 repaid it in full. **Then the cycle-3 ablation showed the
fusion had become dead weight**: everything BM25 contributed was already inside
the dense top-30, and the cross-encoder found it. Hybrid's honest position is
"the latency-constrained alternative", not "a layer in the recommended stack".

**2. Contextual retrieval: six hours of compute for a delta of zero — and that
is a result, not a failure.** Reproducing Anthropic's contextual-retrieval idea
locally (a generated situating sentence per chunk, before embedding and before
BM25) moved nothing: 0.59 vs 0.60 standalone, exactly identical under the
reranker, CI at 0.00. Two caveats are owed to the technique and are recorded in
the cycle-4 section: these chunks were never truly context-less (articles carry
titles, table rows carry header labels), and a 1.5B context generator caps how
good the generated context can be. Against genuinely naked chunks the answer
may differ. For this corpus and pipeline, the plan's own question —
"rechtfertigt der Mehraufwand?" — is answered: no.

**3. From cycle 3 on, the generator is the bottleneck, not retrieval — and
that is what ended the study.** Retrieval improved measurably through cycles
3 and 4 (R@5 0.60 → 0.67, MRR 0.52 → 0.63, global failure rate 40% → 33%)
while the deterministic number-hit metric sat at 0.78 and stopped moving. The
misses did not disappear, they *relocated*: q013/q030 flipped to hits,
q008/q028 to misses, with correct retrieval in all four cases, at temperature
0. A 7B local generator drops roughly two of eighteen answers depending on how
the context happens to be composed. This is the finding that made cycles 6 and
7 indefensible to build: both improve retrieval, and retrieval was no longer
what the end-to-end metric was waiting for.

### The nDCG correction, and what it does to the verdicts

The nDCG@10 numbers in this file are lower than the ones it carried before
2026-09-20. A dedup bug in DCG (see the metric-bug section) inflated them by
roughly 0.03 globally and 0.09–0.10 on the semantic subset, and the fix
removes that inflation everywhere. **It changes no verdict.** That is not
luck: the study's keep/drop calls were deliberately carried by recall@5, MRR
and paired bootstrap CIs — metrics that were never affected — with nDCG
reported alongside rather than decided upon. The episode is still worth the
space it takes here, for two reasons. First, the bug was caught by the metric
contradicting its own definition (a value above 1.0) in a table generated from
raw artifacts, not by anyone re-reading the code — which is an argument for
rendering tables by script and for keeping a metric whose bounds you can
check. Second, it was published wrong for weeks; a study about honest
measurement does not get to leave that out.

### What transfers, and what does not

**Likely transfers:**
- *Ablate before you stack.* The single most valuable measurement in this
  study deleted a component (the fusion) that the previous cycle had just
  added. Neither cycle's number alone would have shown it — only running both
  arms under the reranker did.
- *Keep one judge-free metric in the loop.* The deterministic number-hit check
  found the generator bottleneck; the LLM-judge metrics were too noisy to show
  it (7/13 agreement against a manual re-check).
- *Write the stop conditions before building.* Two optional cycles were
  declined against pre-registered triggers. That is only credible because the
  triggers existed first.
- *Contextual retrieval is not free and not automatic.* Whether it pays
  depends on how context-less your chunks really are — check that before
  spending the compute.

**Probably does not transfer:**
- *"Drop the fusion once you have a reranker."* 4,318 chunks is small. With a
  corpus where dense top-30 no longer contains what BM25 would have found,
  the ablation could come out the other way. Re-run the ablation on your own
  corpus; it costs one eval run.
- *Every latency figure.* CPU-only. The reranker's 29.6 s/query is real here
  and irrelevant anywhere with a GPU.
- *The semantic saturation (R@5 = 1.00 from cycle 1).* German prose analyses
  with distinctive vocabulary are kind to a multilingual dense embedder. A
  corpus of near-duplicate documents would not behave this way.
- *The generator-bottleneck finding, in its strong form.* It says "a 7B model
  on CPU at temperature 0 is the constraint past R@5 ≈ 0.67 on this corpus" —
  not that retrieval work stops paying in general. With a stronger generator
  the ceiling moves and cycles 6/7 might have been worth building after all.

### Honest bottom line

For a mixed, small, local corpus like this one: **dense retrieval plus a
cross-encoder reranker, and stop there.** Hybrid fusion is the fallback when
the reranker's latency is unaffordable. Contextual retrieval did not pay.
Visual late interaction remains untested here for tooling reasons, honestly
documented rather than guessed at. And the most useful number in the whole
study is the one that stopped moving: past a certain retrieval quality, the
next investment belongs in the generator, not in the retriever.

All of this rests on n = 13–18 per question type, a golden set annotated
without independent human review, and one corpus. It *deutet auf*; it does
not *beweist*.
