# Scouting-RAG

**A measured comparison study of retrieval techniques — not a RAG demo.**

Five retrieval stacks — plus a closed-book floor and one ablation — were built
one at a time over the same mixed football-scouting corpus (prose analyses,
season stat tables, rendered stat sheets), and each was measured against the
same 59-query golden set before the next one was allowed to exist. The deliverable is the answer to a question
most RAG write-ups skip: *which technique actually earns its cost, on which
question type, and by how much?*

Everything runs locally and CPU-only. No paid APIs, no cloud GPU, no vendor
keys anywhere in the pipeline. That constraint is deliberate and it shapes the
latency numbers — read them as honest CPU measurements, not as production
figures.

## The answer, in one table

| Cycle | Technique | Recall@5 (global) | Verdict |
|---|---|---|---|
| −1 | Closed book (no retrieval) | – | Floor: 0/18 post-cutoff facts correct |
| 1 | Naive dense (BGE-M3) | 0.60 | **Keep** — the baseline everything must beat |
| 2 | + Hybrid (BM25 + RRF) | 0.60 | **Keep, conditionally** — wins exact-match, taxes semantic@5 |
| 3 | + Cross-encoder reranking | 0.67 | **Keep — recommended stack** |
| 4 | + Contextual retrieval | 0.67 | **Drop** — zero delta for ~6 h of CPU |
| 5 | Visual (ColQwen2 late interaction) | 0.03 global / 0.15 on the visual subset | **Closed without a technique verdict** — reproducible tooling bug |

Text-only cycles cannot exceed an effective global Recall@5 of 0.72 (visual
ground truth is unreachable by design). Read every number against that ceiling,
not against 1.0. Sample sizes per question type are n = 13–18 — every claim in
this repo is phrased as "deutet auf", never "beweist".

### Three findings worth the read

1. **Hybrid search is not free.** BM25 + RRF lifted exact-match (0.83 → 0.89)
   and multi-hop (0.42 → 0.50) but *cost* semantic Recall@5 (1.00 → 0.87).
   The fusion floods top-k with lexically similar but semantically
   interchangeable rows. Reranking healed it completely — and the cycle-3
   ablation then showed that `dense + rerank ≡ hybrid + rerank` on every
   metric. **Once you have a cross-encoder, the fusion buys nothing** at this
   corpus size; it is one component you can delete.
2. **Contextual retrieval bought nothing here.** ~6 h of CPU context
   generation (2,127 chunks) produced a paired-bootstrap delta whose 95 % CI
   is a single point at 0.00. Documented as a negative result, not hidden.
   Two fairness caveats are in `results.md`: our chunks were never truly
   context-less, and the context generator was a 1.5B model.
3. **From cycle 3 on, the generator is the bottleneck, not retrieval.**
   Retrieval kept improving (Recall@5 0.60 → 0.67, MRR 0.52 → 0.63) while
   end-to-end number-hit sat at 0.78 and stopped moving; the misses only
   *shifted* between queries. That measurement is the documented reason
   cycles 6 (agentic) and 7 (GraphRAG) were declined instead of built —
   see `docs/adr/`.

The full narrative, per-question-type tables, bootstrap CIs and the final
synthesis live in [`results.md`](results.md); the same numbers as a
self-contained offline page in [`report/index.html`](report/index.html).

## Method

- **Corpus:** 283 prose articles (394k words), 7 stat CSVs, 84 rendered stat
  sheets — 955k text tokens total. The long-context stop check from the plan
  is answered in [`CORPUS.md`](CORPUS.md): the corpus does not fit a context
  window, so retrieval is load-bearing.
- **Golden set:** 59 queries in `eval/golden_set.jsonl`, typed
  `semantic | exact_match | multi_hop | visual`, with per-query ground truth
  as passages, table rows or images.
- **Chunking-agnostic ground truth:** a retrieved chunk counts as relevant iff
  it overlaps an annotated passage / table row / image (`eval/SCHEMA.md`).
  Changing the chunking strategy between cycles therefore never invalidates
  the eval set — which is what made one-variable-per-cycle possible at all.
- **Primary metrics are judge-free:** Recall@5/@10, Precision@5, MRR,
  nDCG@10 against that ground truth. Secondary generation metrics use a
  deterministic number-hit check plus a local LLM judge, reported next to its
  own measured noise.
- **Every number comes from a committed run** in `eval/results/*.json` and is
  rendered into `results.md` and the report by script
  (`scripts/render_results.py`, `scripts/render_report.py`) — never
  hand-transcribed. That rule exists because hand-transcription drift was
  caught in this very repo.

## Honest limitations

Read these before quoting any single number:

- **The golden set was written and annotated by the same AI that built the
  pipelines.** A 20 % human review sample was prepared
  (`eval/REVIEW_SAMPLE.md`) but never reviewed by a human. Systematic
  annotation bias cannot be ruled out.
- **Judge validation is thin.** The local faithfulness judge agreed with a
  manual re-check on only 7 of 13 cases strictly (10/13 under the
  honest-refusal reading), and the re-check was itself done by Claude, not a
  human. Faithfulness aggregates are indicative; single verdicts are not
  usable.
- **Small samples.** n = 13–18 per question type: one query moves a metric by
  7–8 points.
- **Cycle 5 has no technique verdict.** It was built, run, and closed on a
  reproducible `colpali_engine` / `transformers` weight-loading bug. The 0.15
  Recall@5 measured a broken model, not ColQwen2.
- **A metric bug was found and fixed late** (nDCG@10 exceeded its 1.0 bound
  until 2026-09-20). The fix is in `src/eval_metrics.py` with three regression
  tests; every retrieval eval is re-run against the unchanged indexes and the
  before/after delta is printed in `results.md`. Result files carry an
  `eval_metrics_version` stamp, and any cycle whose nDCG has not been
  recomputed yet is marked in that table — the report will not claim the
  re-run is complete while an artifact on disk says otherwise.

The full versions of all of these are in the Limitations section of
`results.md` and in the report.

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # pinned
cp .env.example .env

# local LLMs (Ollama, https://ollama.com/download)
ollama pull qwen2.5:7b      # generation
ollama pull llama3.1:8b     # faithfulness judge
ollama pull qwen2.5vl:7b    # visual generation (cycle 5)
```

Then, in order (the corpus itself is not shipped — see *Data & licensing*):

| Step | Command | Wall clock (16-core CPU, no GPU) |
|---|---|---|
| Fetch corpus | `python -m scripts.scrape_articles discover` → `… fetch` · `python -m scripts.fetch_stats` · `python -m scripts.render_statsheets` | ~1 h (≥5 s between requests, by policy) |
| Build dense index | `python -m src.embed_index build` | ~106 min (BGE-M3, 4,318 chunks) |
| Retrieval eval (per cycle) | `python -m src.run_eval retrieval --retriever dense --name cycle1_dense_retrieval` | ~1 min |
| …with reranking | `--retriever hybrid_rerank` / `dense_rerank` / `dense_ctx_rerank` | ~30 min (30 cross-encoder passes per query) |
| Generation eval | `python -m src.run_eval rag --retriever dense --name cycle1_rag_k5 --k 5` | ~70 s per query |
| Secondary metrics | `python -m src.run_secondary eval/results/cycle1_rag_k5.json --judge` | ~50 min |
| Contextual index (cycle 4) | `python -m src.contextualize` · `python -m src.build_ctx_index` | ~6 h + ~100 min |
| Visual index (cycle 5) | `python -m src.visual_index build` | ~8.2 h (~350 s per page × 84) |
| Regenerate tables & report | `python -m scripts.render_results` · `python -m scripts.render_report` | seconds |
| Gate | `python -m pytest -q` | ~10 s |

`scripts/render_results.py --check` fails if `results.md` is stale relative to
the eval artifacts — that is the integrity gate against hand-edited numbers.

Qdrant runs **embedded** (`QdrantClient(path=...)`); there is no server to
start. Ollama must be reachable at `localhost:11434` for anything that
generates.

## Repo map

| Path | What it is |
|---|---|
| `PLAN.md` | The binding cycle plan and working mode — verbatim, never edited |
| `PROJECT.md` | Short project card: method, cycle verdicts, stack |
| `results.md` | The comparison tables, per-cycle verdicts, limitations, **final synthesis** |
| `report/index.html` | The same study as one offline HTML page (no JS, no CDN) |
| `CORPUS.md` | Sources, licensing, volumes, long-context stop check |
| `eval/` | Golden set, schema, review samples, raw per-run JSON results |
| `src/` | One module per technique + `run_eval.py` / `run_secondary.py` harness |
| `scripts/` | Corpus acquisition, rendering of results and report |
| `docs/adr/` | Decisions that refine the plan (e.g. why cycles 6/7 were skipped) |
| `docs/blog-draft.md` | Write-up draft of the findings |

## Data & licensing

`data/` is **gitignored by design**. The prose corpus consists of scraped
publicly accessible analysis articles licensed for private, non-commercial
research use only — it is never committed and never redistributed.
Reproducibility comes from the scraper code, the committed URL manifest
(`corpus_urls.jsonl`) and the fetch dates documented in `CORPUS.md`. Stat
tables come from OpenLigaDB and worldfootballR/FBref extracts; the stat sheets
are rendered by this repo from those numbers. Access controls were never
worked around — sources that blocked crawling were dropped and the drops are
listed in `CORPUS.md`.

The saved `eval/results/*_rag_*.json` runs keep only the first 200 characters of each retrieved context
(`context_texts`), so no article text is redistributed. Re-running a run regenerates the full texts locally.
