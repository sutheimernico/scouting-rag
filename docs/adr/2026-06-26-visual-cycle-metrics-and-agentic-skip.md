# ADR: Visual-cycle metric framing and the decision to skip cycle 6 (agentic)

- **Date:** 2026-06-26
- **Status:** accepted
- **Phase:** cycle 5 (visual retrieval) + study close-out
- **Relation to PLAN.md:** refines how cycle-5 metrics are *read* and records why
  the optional cycles 6/7 are not built. Does not change any cycle's scope or
  the measured-delta principle.

## Context

Per the AUTOPILOT self-improvement mandate (once per phase), the cycle-5
methodology and the optional-cycle triggers were re-examined against current
best practice before writing the cycle-5 verdict and the final synthesis.

## Decision 1 — visual subset is a known-item retrieval task; Recall@k + MRR are the informative metrics

Each of the 13 visual golden-set queries has **exactly one** relevant stat-sheet
image as ground truth. Under single-relevant-document conditions:

- **Recall@5 / Recall@10** are the meaningful signal ("did the one right sheet
  make the shortlist") and are reported as primary.
- **MRR** is the cleanest rank-quality number and is reported as primary.
- **Precision@5** is capped at 1/k = 0.20 — a *perfect* system scores 0.20, so
  the raw number invites misreading. **nDCG@10** with single binary relevance is
  a monotone function of the hit rank, i.e. it carries the same information as
  MRR. Both are still filled in the results tables for column-consistency with
  cycles 1–4, but flagged as non-informative for this task.

Consequence: the visual verdict reports **counts** ("X of 13 retrieved at
rank 1") next to rates, because at n=13 a rate alone overstates precision.

## Decision 2 — brute-force MaxSim (no ANN/PLAID) is the correct setup here

At 84 pages, exact brute-force MaxSim in torch *is* the retrieval-quality upper
bound; ANN/PLAID/quantization are latency approximations that can only lose
recall. Skipping them strengthens the validity of the retrieval-quality
comparison. The honest caveat is the inverse: the measured per-query CPU cost is
not representative of an indexed production deployment, and the result says
nothing about scaling.

## Decision 3 — ColQwen2 on self-rendered sheets is in-distribution → ceiling-inflated

ColPali/ColQwen2's design target is exactly rendered chart/table/document pages
(the ViDoRe benchmark). Our 84 sheets are a single clean self-rendered template
with no scan noise or layout diversity, so high visual recall is partly the
model and partly an easy in-distribution setting. Flagged as a validity threat
in the synthesis, not advertised as a strength.

## Decision 4 — VLM answer quality measured by deterministic number-hit, not the text-faithfulness judge

The cycle-5 VLM reads images; there is no retrieved *text* context, so the
llama3.1:8b text-faithfulness judge does not apply. The deterministic number-hit
metric (do all reference numbers appear in the answer?) is the defensible
primary answer-quality signal for "read percentile X off the sheet" queries.
Reported both end-to-end and (where retrieval succeeded) conditioned on a
correct top-1 retrieval, to separate retrieval from chart-reading. Failure mode
documented: number-hit cannot catch a right-number-wrong-stat answer; treated as
indicative, not a faithfulness guarantee.

## Decision 5 — cycles 6 (agentic) and 7 (GraphRAG) are NOT built

PLAN.md gates both cycles behind a trigger condition. Cycle 6's trigger is
"multi-hop queries run demonstrably weak in the eval." They do run weak
(multi-hop R@5 plateaus at 0.58), **but the cycle-3 finding is that the
bottleneck past cycle 3 is the generator/answer-composition step, not
retrieval**: number-hit plateaued at 0.78 while retrieval kept improving, and
the residual multi-hop retrieval misses are structural (the needed information
is in no chunk). Query decomposition (CRAG-style) addresses *retrieval*
coverage, so it would not move the measured multi-hop metric on this corpus.
Building it would be effort against a non-cause. Cycle 7's trigger (global
corpus-wide provenance queries) does not appear in the golden set at all.

Both are recorded as **deliberate, trigger-justified scope decisions**, not
omissions — consistent with the "no over-building" principle.

## Consequences

- The cycle-5 verdict and final synthesis report Recall@k + MRR + counts as the
  visual primary, with Precision/nDCG shown but caveated.
- No further cycles are built; the study closes after the cycle-5 verdict and
  the final synthesis in `results.md`.
