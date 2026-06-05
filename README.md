# Scouting-RAG

A measured comparison study of retrieval techniques (naive vector → hybrid → reranking → contextual retrieval → visual/ColPali → optionally agentic) over a mixed football-scouting corpus: prose analysis articles, season stat tables, and visual stat sheets.

The deliverable is not "a RAG pipeline that runs" but a comparison table with per-question-type deltas, costs, and latency for every technique — see `results.md`.

## Key documents

| File | Purpose |
|------|---------|
| `PLAN.md` | Binding project plan: cycles, working mode, iron principles |
| `docs/superpowers/specs/2026-06-05-scouting-rag-corpus-eval-design.md` | Design decisions: corpus sourcing, eval methodology, local-only infra |
| `CORPUS.md` | Corpus sources, licenses, volumes, token check (written in cycle 0) |
| `results.md` | The comparison table — one row per cycle, incl. closed-book baseline |

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# Ollama (local LLMs): https://ollama.com/download — then:
ollama pull qwen2.5:7b && ollama pull llama3.1:8b && ollama pull qwen2.5vl:7b
```

Everything runs locally on CPU. No paid APIs. Long-running steps (eval runs, indexing) are designed as overnight batches.

## Data & licensing

`data/` is **gitignored by design**: the prose corpus consists of scraped publicly accessible analysis articles licensed for private use only — it must never be committed or redistributed. Reproducibility comes from the scraper code, the URL list, and fetch dates documented in `CORPUS.md`. Stat tables and self-rendered stat sheets are derived from documented public sources.
