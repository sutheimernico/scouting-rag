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

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| −1 | Closed book (no retrieval) | – | – | – | – | – |
| 1 | Naive dense (BGE-M3) | 0.60 | **1.00** | 0.83 | 0.42 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.60 | 0.87 | **0.89** | **0.50** | 0.00 |
| 3 | + Reranking (cross-encoder) | **0.67** | **1.00** | **0.94** | **0.58** | 0.00 |
| 4 | + Contextual retrieval | | | | | |
| 5 | Visual (ColQwen) | | | | | |
| 6 | Agentic (optional) | | | | | |

## Primary: Recall@10 / Precision@5 / MRR / nDCG@10

_Same table layout as Recall@5 — filled per cycle._

### Recall@10

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| 1 | Naive dense (BGE-M3) | 0.66 | 1.00 | 0.89 | 0.62 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.66 | 1.00 | 0.89 | 0.62 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.69 | 1.00 | 0.94 | 0.65 | 0.00 |

### Precision@5

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| 1 | Naive dense (BGE-M3) | 0.15 | 0.24 | 0.17 | 0.17 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.16 | 0.20 | 0.18 | 0.20 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.18 | 0.25 | 0.19 | 0.22 | 0.00 |

### MRR

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| 1 | Naive dense (BGE-M3) | 0.53 | 0.79 | 0.64 | 0.62 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.52 | 0.69 | 0.65 | 0.65 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.63 | 0.86 | 0.84 | 0.69 | 0.00 |

### nDCG@10

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| 1 | Naive dense (BGE-M3) | 0.56 | 0.95 | 0.70 | 0.49 | 0.00 |
| 2 | + Hybrid (sparse + RRF) | 0.55 | 0.86 | 0.72 | 0.51 | 0.00 |
| 3 | + Reranking (cross-encoder) | 0.65 | 1.00 | 0.89 | 0.56 | 0.00 |

## Secondary: generation quality (judge-free number-hit + local judge)

Number-hit = all reference numbers appear in the answer (deterministic,
exact-match subset). Faithful (strict) = judge says every claim is
context-supported. Honest = supported OR honest refusal (the judge applied
the refusal rule inconsistently, so both readings are reported).

| Cycle | Number-hit exact-match (n=18) | Faithful strict (n=59) | Honest (n=59) | Refusal rate | Manual check (n=13) |
|-------|-------------------------------|------------------------|---------------|--------------|---------------------|
| −1 | **0.00** | n/a (no context to be faithful to) | n/a | – | – |
| 1 | **0.72** | 0.66 | 0.95 | 0.31 | done (Claude, not human — see below) |
| 2 | **0.78** | 0.76 | 0.98 | 0.22 | – |
| 3 | **0.78** | 0.73 | 0.98 | 0.25 | – |

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
