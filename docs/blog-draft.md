---
title: "What I measured when I stopped trusting RAG advice"
subtitle: "Six retrieval stacks, one corpus, 59 queries — and the two techniques that did not earn their cost"
status: draft — Nico to refine (voice, length, publication target)
date: 2026-09-20
source: https://github.com/sutheimernico/RAG-Projekt
---

_(draft — Nico to refine. Every number below is traceable to a committed
eval artifact in `eval/results/`; nothing here is estimated. Open editorial
questions are listed at the bottom.)_

## The setup

Most RAG write-ups are architecture tours. You get a diagram, a list of
techniques — hybrid search, reranking, contextual retrieval, late-interaction
visual retrieval — and an implicit promise that stacking them makes things
better. What you almost never get is the number that matters: *how much
better, for which kind of question, at what cost?*

So I built the measurement instead of the product.

The corpus is a mixed football-scouting knowledge base: 283 German prose
analyses (394k words), seven season stat tables, and 84 self-rendered player
stat sheets as images — about 955k text tokens. Mixed on purpose, because
retrieval techniques behave very differently on flowing prose than on a naked
table row, and I wanted that difference to show up in the data rather than in
my intuition.

The rules I gave myself up front, and did not renegotiate afterwards:

- **One new technique per cycle.** Never two changes at once, or the delta
  stops being attributable.
- **Corpus and evaluation set exist before any retrieval code.** No moving
  the target.
- **A technique stays only if it proves its delta.** If it does not, it gets
  documented as a negative result and removed.
- **Everything local, CPU-only.** No paid APIs, no cloud GPU. This made some
  runs painfully slow, and it kept every number honest about what the thing
  actually costs.

Evaluation is 59 hand-typed queries (`semantic`, `exact_match`, `multi_hop`,
`visual`) with per-query ground truth annotated as passages, table rows or
images. Crucially, ground truth is **chunking-agnostic**: a retrieved chunk
counts as relevant if it overlaps an annotated passage. That one design
decision is what made the whole study possible — I could change the chunking
strategy between cycles without invalidating the evaluation set.

## Finding 1: hybrid search is not free

Received wisdom says: add BM25 to your dense retrieval, fuse with Reciprocal
Rank Fusion, get the best of both. That is half true.

BM25 + RRF did exactly what it says on the tin where queries carry specific
tokens: exact-match Recall@5 went 0.83 → 0.89, multi-hop 0.42 → 0.50. A query
about "PPDA" — a domain abbreviation the dense embedder simply does not place
well — went from a miss to a perfect answer.

It also *cost* me something nobody mentions: semantic Recall@5 dropped from a
saturated 1.00 to 0.87. Global recall did not move at all. Under fusion, a
question like "which club won…" floods the top-k with eighteen
interchangeable table rows, because no single row carries rank semantics —
and the one row that actually answers the question gets pushed out.

So hybrid was kept, but *conditionally*: the semantic regression was booked
as a debt for the next cycle to repay.

## Finding 2: once you have a reranker, the fusion is dead weight

Cycle 3 added a cross-encoder reranker (`bge-reranker-v2-m3`) over the top-30.
It was the strongest cycle of the study: global Recall@5 0.60 → 0.67 (against
an effective ceiling of 0.72 — the visual ground truth is unreachable for
text retrievers by design), semantic recovered fully to 1.00, exact-match rose
to 0.94, MRR 0.52 → 0.63. Global retrieval failure dropped from 40 % to 33 %.

Then I ran the ablation that the hype cycle skips: **dense + rerank versus
hybrid + rerank.** They are identical. On every metric, on every subset. The
paired bootstrap on the global Recall@5 delta is a single point at 0.00.

Read plainly: at this corpus size, everything BM25 contributed was already
sitting somewhere in the dense top-30, and the cross-encoder found it. Hybrid
retrieval's standalone value is real — but only in a setup that cannot afford
a reranker. If you can, you have one component fewer to build, tune and
operate.

The reranker is not free either, and this is where CPU-only honesty pays off:
retrieval latency went from 0.38 s to 29.6 s per query, because 30
cross-encoder passes on a CPU is exactly as slow as it sounds. On a GPU this
is sub-second. I report the number I measured, not the number I would like.

## Finding 3: contextual retrieval bought nothing — for six hours of compute

Cycle 4 implemented Anthropic-style contextual retrieval: prepend an
LLM-generated situating sentence to every chunk before embedding and before
BM25 indexing. 2,127 article chunks, a 1.5B local model, roughly six hours of
CPU, plus another 100 minutes to re-encode the index.

Result: **zero.** Standalone, dense+ctx scored 0.59 against plain dense's 0.60
— inside one-query noise. Under the reranker, contextual retrieval and plain
reranking are identical on every metric and every subset; the bootstrap CI of
the delta is a degenerate interval at 0.00.

Two caveats I owe the technique, both in the repo: my chunks were never truly
context-less (articles carry titles, table rows carry header labels), and a
1.5B context generator caps how good the generated context can be. Contextual
retrieval against genuinely naked chunks may well behave differently.

For *this* corpus and *this* pipeline, the answer to the plan's own question —
"does the extra cost justify itself?" — is no. Dropped, documented, kept in
the write-up. A negative result that cost six hours is still a result; the
failure mode would have been not measuring it and shipping it anyway.

## Finding 4: at some point retrieval stops being the problem

This is the finding I did not plan for and value most.

From cycle 3 onward, retrieval kept improving and end-to-end answer quality
did not. The deterministic number-hit metric (does the answer contain the
reference number?) sat at 0.78 from cycle 2 through cycle 3, while Recall@5
climbed 0.60 → 0.67. The individual misses *moved* — two queries flipped to
hits, two flipped to misses — with correct retrieval in all four cases, at
temperature 0.

In other words: the 7B local generator drops roughly two of eighteen answers
depending on how the context happens to be composed, and no amount of better
retrieval fixes that.

That measurement is also why this study does **not** contain an agentic RAG
cycle. The trigger condition I had pre-registered (multi-hop demonstrably
weak) was met — multi-hop recall stayed the worst non-visual subset. But
query decomposition improves *retrieval*, and retrieval was no longer the
binding constraint. Building it would have produced a nicer architecture
diagram and no measurable improvement. Declining it is written up as a
decision record, not omitted quietly.

## The cycle that did not work, and stays in the paper anyway

Cycle 5 was meant to be the showpiece: ColQwen2 late-interaction retrieval
over the stat-sheet images, no OCR, no chunking, straight from pixels.

It was built, the 84-page index was computed (about 8 hours of CPU), the
evaluation ran, and the result was terrible: Recall@5 of 0.15 on the visual
subset, zero correct top-1 hits.

The honest move was to find out *why* before writing it up as a technique
verdict — and the why turned out to be mine, not the model's. Inspecting the
loaded state dict showed the language backbone's embedding and final-norm
layers arriving **randomly initialized**: `language_model.norm.weight` with
mean exactly 1.0 and standard deviation exactly 0.0, `embed_tokens` with a
textbook default init. A module-naming drift between `colpali_engine` and a
newer `transformers` silently dropped those weights on load. Pip's version
constraints do not catch it, because it is a runtime key-naming mismatch, not
a version-range violation.

So the number is real and the model that produced it was not the model the
design called for. Cycle 5 is closed as "attempted, root-caused, closed
without a technique verdict", with the state-dict evidence committed. It would
be much easier to publish 0.15 as "ColQwen2 underperforms on stat sheets".
That claim would be false.

## What I would take to the next project

- Ablate the stack you are proud of. The cycle-3 ablation deleted a component
  I had just spent a cycle building.
- Measure the boring metric. A deterministic number-hit check found the
  generator bottleneck that four judge-based metrics were too noisy to show.
- Write down the stop conditions before you build. Two optional cycles were
  declined on evidence instead of on enthusiasm, and that is only defensible
  because the criteria existed beforehand.
- Fix your metrics in public. This study shipped with an nDCG implementation
  that could exceed 1.0 — visible in the published tables for weeks — because
  DCG credited every rank matching the same ground-truth entry. It is fixed,
  regression-tested, the evals are re-run against the unchanged indexes, and
  the before/after is in the repository. It changed no verdict — because the
  verdicts were deliberately carried by metrics that bug could not touch. The interesting part is not the bug; it is that the metric was
  transparent enough to catch itself.

---

### Open editorial questions for the content pass

- German or English? The repo is English; Nico's portfolio audience may prefer
  German.
- Length: this is ~1,250 words. A portfolio version could cut findings 1–2
  into one section.
- Which single chart to include: Recall@5 per cycle, or the failure-rate
  framing (40 % → 33 %)? The report renders both.
- The nDCG before/after numbers should be quoted exactly from `results.md`
  once the section is final.
