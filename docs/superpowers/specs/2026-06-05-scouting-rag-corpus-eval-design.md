# Design Spec: Corpus, Evaluation & Local-Only Infrastructure

- **Date:** 2026-06-05
- **Status:** awaiting user approval
- **Relation to PLAN.md:** This spec fills the gaps PLAN.md leaves open (corpus sourcing, eval mechanics, model/infra concretes) and documents agreed amendments. Everything not mentioned here applies unchanged as written in PLAN.md.

## Context

Scouting-RAG is a measured comparison study of retrieval techniques over a mixed football-scouting corpus (prose reports, stat tables, visual stat sheets). The deliverable is a comparison table plus per-question-type analysis of which technique earns its keep. See PLAN.md for cycles, working mode, and iron principles.

## Decisions made (2026-06-05, with Nico)

| # | Decision | Chosen option | Key trade-off accepted |
|---|----------|---------------|------------------------|
| D1 | Corpus strategy | Real public data (over fictional-league synthetic) | LLM parametric knowledge about real players can blur generation metrics → mitigations M1–M3 below |
| D2 | LLM provider | Local only via Ollama, no paid APIs | Small quantized models are too noisy as LLM-judge → eval redesign (Section 2); everything runs in time instead of money (overnight batches) |
| D3 | Prose source | Scrape real analysis articles (over Wikipedia-only or synthetic-grounded) | Corpus is licensed for private use only: never committed, never redistributed; player coverage is article-driven |

### Mitigations for parametric-knowledge contamination (D1)

- **M1 — Closed-book baseline ("cycle −1"):** generator answers the golden set with zero retrieved context. This measures what the model already knows and becomes the reference line every RAG cycle must beat. One extra row in `results.md`.
- **M2 — Judge-free retrieval metrics as primary measure** (see Section 2): chunk-level ground truth is unaffected by what the generator knows.
- **M3 — Data bias against prior knowledge:** prefer season 2025/26 stats (post-cutoff for common models) and include 2. Bundesliga players, not only stars.

## 1. Corpus design

Three document classes, all stored under `data/` (gitignored).

### 1a. Prose: scraped analysis articles

- Sources: freely accessible football-analysis sites with player-centric content, e.g. Spielverlagerung.de (DE), Total Football Analysis player analyses (EN), Abseits.at (DE). Final source list goes into `CORPUS.md`.
- Mixed German/English corpus, German queries. BGE-M3 is multilingual; cross-lingual retrieval is a realistic, documented property of the study.
- Target volume: ~100–200 articles.
- Extraction: `trafilatura` (new dependency; purpose-built for article text extraction).
- **Scraping rules (binding):** only freely accessible pages (no paywall circumvention), respect robots.txt and TDM opt-outs (§ 44b UrhG), honest user agent, rate limit ≥ 5 s between requests, fetch once and cache locally.
- **Licensing posture:** what gets versioned is the URL list + fetch date + scraper code, never the article text. The corpus is for private use in this project only and must never be committed or redistributed. Public artifacts (code, `results.md`, analysis) contain no third-party text beyond short quotes.

### 1b. Tables: season stats 2025/26

- Player season stats (standard / shooting / passing / defense) for Bundesliga + 2. Bundesliga via FBref CSV exports; Kaggle dump as fallback. Source and fetch date documented in `CORPUS.md`.
- Stored as CSV in `data/`; for indexing, converted to per-row Markdown chunks carrying header context (league, season, table type).

### 1c. Visual stat sheets: self-rendered

- Rendered from 1b with `mplsoccer` (new dependency): radar charts and pizza plots; heatmaps only if StatsBomb Open Data event data is added for a player subset later.
- Target volume: 60–100 PNG pages.
- Self-rendering keeps licensing clean and gives exact per-image ground truth (we know which numbers each sheet encodes).

### Known risk (documented, accepted)

Player coverage is article-driven and skewed toward written-about players. Consequence: the golden set is built **corpus-driven** — first acquire the corpus, then derive queries from what it actually contains. `CORPUS.md` records the coverage skew.

## 2. Evaluation methodology (amendment to PLAN.md Section 4 "Eval: RAGAS oder DeepEval")

Rationale: with local-only models (D2), an LLM-judge on a 7–8B quantized model is too noisy to detect cycle deltas at n=12–15 per subset. RAGAS-style LLM-judged context metrics are a workaround for missing chunk-level ground truth — we have ground truth, so we measure directly.

### Primary metrics (judge-free, deterministic)

- Recall@k, Precision@k, MRR, nDCG@10 against hand-annotated ground truth (k = 5 and 10).
- Ground truth is annotated **chunking-agnostic** as (doc_id, passage quote) — chunking only happens in cycle 1, and chunk strategies may evolve across cycles. A retrieved chunk counts as relevant iff it overlaps a ground-truth passage. This keeps the golden set stable across cycles.
- Own implementation (~50 lines), unit-tested, seeded where applicable. Replaces RAGAS context metrics and PLAN.md's Pass@k (Recall@k covers it).

### Secondary metrics (generation quality, reported with caution)

- Faithfulness + answer quality via local judge: `llama3.1:8b` judges, `qwen2.5:7b` generates — separation across model families instead of providers; documented as a limitation.
- Manual spot-check n=10 per cycle to calibrate the judge.
- Judge noise is quantified once via test–retest on 10 queries and reported alongside every secondary metric.

### Baselines and golden set

- **Cycle −1 (closed book):** generator without context, logged in `results.md` like any cycle.
- Golden set: 50–60 queries (raised from 30–50), corpus-driven; subsets exact-match / visual / multi-hop sized ≥ 12 each, remainder semantic. Stored in `eval/golden_set.jsonl` with type labels and ground-truth passages (doc_id + quote).
- Annotation process: Claude proposes relevant chunks per query, Nico reviews a 20% sample ("inter-rater light"); process and its limits documented in the final analysis.

## 3. Models & infrastructure (all local, CPU-only)

Environment (checked 2026-06-05): WSL2, Python 3.12, 15 GB RAM, ~950 GB disk, **no GPU**, Ollama not yet installed, Docker without WSL integration.

| Role | Model | Runtime |
|------|-------|---------|
| Generator | `qwen2.5:7b` | Ollama |
| Judge | `llama3.1:8b` | Ollama |
| VLM (cycle 5) | `qwen2.5vl:7b` | Ollama |
| Embeddings (dense+sparse) | `BAAI/bge-m3` | HF local |
| Reranker (cycle 3) | `BAAI/bge-reranker-v2-m3` | HF local |
| Visual retrieval (cycle 5) | ColQwen2 via `colpali-engine` | HF local |

- **Vector store:** Qdrant embedded mode (`QdrantClient(path=...)`) — supports dense, sparse and multivector; no Docker needed. Adequate at our corpus size; revisit only if it becomes a measured bottleneck.
- **RAM plan (15 GB):** pipeline phases run sequentially — retrieval (BGE-M3 loaded) finishes and frees memory before generation (Ollama loads); Ollama `keep_alive` tuned so models unload between phases.
- **Time instead of money:** eval runs, cycle-4 context generation, and cycle-5 indexing run as overnight batches (~5–10 tok/s generation expected). Latency figures in `results.md` are honest CPU numbers and labeled as such; they are not production-representative.
- **CPU long-context note:** prompt processing on CPU makes large contexts impractically slow. This effectively answers PLAN.md's cycle-0 long-context stop check for the local setup; the token count in `CORPUS.md` still documents corpus size properly.
- Expected quality caveat (cycle 5): chart-reading on a 7B VLM is shaky; the ColPali retrieval delta (primary metric) is unaffected, generation quality reported as secondary.

## 4. Repository layout & cycle-0 execution order

```
scouting-rag/
├── PLAN.md                  # verbatim project plan (binding)
├── CORPUS.md                # sources, licenses, volumes, token check
├── results.md               # comparison table incl. cycle −1 row
├── README.md
├── requirements.txt         # pinned
├── .env.example             # OLLAMA_HOST, model names
├── docs/superpowers/specs/  # this spec
├── eval/golden_set.jsonl
├── scripts/                 # scrape_articles, fetch_stats, render_statsheets
├── src/                     # pipeline code (cycle 1+)
└── data/                    # gitignored corpus
```

Cycle-0 order: repo scaffold (venv, pinned deps, .env template) → Ollama install (needs sudo once) + model pulls → corpus acquisition (1a–1c) → token count + long-context check in `CORPUS.md` → golden set → `results.md` skeleton.

## Summary of amendments to PLAN.md

1. Metric set: judge-free IR metrics (Recall@k, Precision@k, MRR, nDCG@10) replace RAGAS/DeepEval context metrics and Pass@k as primary; faithfulness/answer quality become secondary via local judge + manual sample (Section 2).
2. `results.md` gains a closed-book baseline row (cycle −1).
3. Golden set raised to 50–60 queries with minimum subset sizes (≥ 12 for exact-match, visual, multi-hop).
4. Generator LLM is local via Ollama, not a paid API ("Generierungs-LLM via API" in PLAN.md Section 4 is amended accordingly).
5. Corpus stays private (gitignored); reproducibility via scraper code + URL list + fetch dates instead of committed data.
