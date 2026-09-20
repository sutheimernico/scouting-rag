# PROJECT.md — scouting-rag

## What this is

A measured comparison study of retrieval-augmented generation techniques,
not a product. The corpus is a mixed football-scouting knowledge base
(prose scouting reports, statistics tables, visual stat sheets); the
deliverable is a reproducible answer to "which retrieval technique earns
its cost, for which question type, and by how much" — see `results.md`
for the full numbers and `PLAN.md` for the binding cycle plan.

Everything runs locally, CPU-only, on free/local infrastructure: no paid
APIs, no cloud GPU. That constraint is deliberate (see Method) and shapes
several results (e.g. reranker/context-generation latency numbers are
CPU-honest, not production-representative).

## Method

One new retrieval technique per cycle, each measured against the golden
evaluation set (`eval/golden_set.jsonl`, 59 hand-annotated queries typed
`semantic | exact_match | multi_hop | visual`) before the next cycle is
built. Ground truth is chunking-agnostic (a chunk is relevant iff it
overlaps an annotated passage/table-row/image — see `eval/SCHEMA.md`), so
changing the chunking strategy across cycles never invalidates the eval
set. Primary metrics are judge-free IR metrics (Recall@5/10, Precision@5,
MRR, nDCG@10) against that ground truth (nDCG's DCG deduplicates repeated
coverage of one ground-truth entry — fixed 2026-09-20, all cycles re-run,
before/after in `results.md`); secondary metrics use a local
LLM judge (`llama3.1:8b`) for faithfulness/refusal, reported next to its
own measured test–retest noise.

Iron principles (binding, see `PLAN.md` §3): corpus and golden set exist
before any retrieval technique is built; every technique must prove its
delta or it is documented and dropped; changes are never bundled (one
variable per cycle, so the delta is attributable); sample sizes are
always stated and hedged (n≈13–18 per question type: "deutet auf", not
"beweist"); every number in `results.md` comes from an actual run — never
invented, estimated, or extrapolated.

## Cycle overview and verdicts

| Cycle | Technique | Verdict | Why |
|-------|-----------|---------|-----|
| −1 | Closed book (no retrieval) | baseline | number-hit 0.00 post-cutoff; establishes the floor |
| 1 | Naive dense (BGE-M3) | **keep** | the baseline every later cycle must beat |
| 2 | + Hybrid (BM25 + RRF) | **keep, conditionally** | wins on exact-match/multi-hop where tokens are specific; semantic@5 regresses (recovers at k=10); superseded once reranking lands |
| 3 | + Cross-encoder reranking | **keep — recommended stack** | strongest cycle; heals the cycle-2 semantic regression; ablation shows dense+rerank ≡ hybrid+rerank, so the fusion adds nothing once a reranker is present |
| 4 | + Contextual retrieval | **drop** | zero measurable delta over hybrid+rerank despite ~6h CPU cost for context generation; documented as a negative result, not a failure to reach the bar |
| 5 | Visual (ColQwen2 late interaction) | **inconclusive — tooling-blocked, closed** | index built and evaluated (Recall@5 0.15, n=13), but the ColQwen2 checkpoint loads with its language-model backbone randomly initialized (`colpali_engine`/`transformers` key-naming drift, proven from the state dict) — the run measured a broken model, not the technique. A remap-shim fix path is specified and was time-capped by the closing plan; the cap governed, so the cycle is closed without a technique verdict rather than left open. See `results.md` cycle-5 section |
| 6 | Agentic RAG (optional) | **not built** | trigger condition (multi-hop demonstrably weak) is met, but the cycle-3 finding is that the generator, not retrieval, is the end-to-end bottleneck past cycle 3 — decomposition would not move the measured metric (`docs/adr/2026-06-26-visual-cycle-metrics-and-agentic-skip.md`) |
| 7 | GraphRAG (optional) | **not built** | trigger condition (global cross-corpus provenance queries) does not occur in the golden set |

The study is closed at cycle 4: the recommended stack is dense retrieval +
cross-encoder reranking, hybrid fusion is the reranker-free fallback,
contextual retrieval is a documented negative result, and cycles 5–7 end
without technique verdicts for the reasons in the table. The full reasoning
is in the closing synthesis of `results.md`.

From cycle 3 onward, the generator (not retrieval) is the measured
end-to-end bottleneck: retrieval kept improving through cycles 3–4 while
answer-quality metrics plateaued. This finding is the documented reason
cycles 6/7 were declined rather than built speculatively.

## Stack

Python, pinned dependencies (`requirements.txt`). Qdrant embedded
(`QdrantClient(path=...)`, no server) for dense/hybrid indexing; BGE-M3
for dense + sparse embeddings; `rank_bm25` for the sparse side of hybrid
retrieval; `bge-reranker-v2-m3` cross-encoder for reranking; ColQwen2
(`vidore/colqwen2-v1.0`, `colpali_engine`) with brute-force torch MaxSim
for visual late-interaction retrieval; Ollama running `qwen2.5:7b`
(generation), `qwen2.5vl:7b` (visual generation), `qwen2.5:1.5b` (cycle-4
context generation), `llama3.1:8b` (faithfulness judge) — all local, no
paid API calls anywhere in the pipeline.

## Where things live

- `PLAN.md` — binding cycle plan and working mode (verbatim, never edited)
- `results.md` — the measured comparison table, deltas, verdicts, the
  collected limitations, and the **final synthesis** (PLAN.md §5) that closes
  the study
- `docs/blog-draft.md` — write-up draft of the findings (awaiting Nico's voice pass)
- `CORPUS.md` — corpus sources, licensing, volume, the long-context check
- `eval/golden_set.jsonl` + `eval/SCHEMA.md` — the eval set and its schema
- `eval/results/*.json` — raw per-cycle run outputs (retrieval, generation, secondary metrics)
- `src/` — one module per retrieval/generation technique, `run_eval.py` / `run_secondary.py` as the eval harness
- `docs/adr/` — decisions made mid-project that refine (not override) `PLAN.md`
- `report/index.html` — self-contained static study report generated from `eval/results/`
