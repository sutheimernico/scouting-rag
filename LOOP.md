# scouting-rag — LOOP (per-iteration prompt for the autonomous build agent)

> **Status 2026-09-20: the study is closed.** Cycles −1…4 are verdicted, cycle 5
> is closed without a technique verdict (tooling-blocked, see
> `docs/colqwen2-load-evidence.md`), cycles 6/7 were declined by ADR, and the
> final synthesis PLAN.md §5 mandates is written. There is no open build task.
> Do **not** open a new cycle — the study's own Iron Principles and ADR forbid
> it. The only mechanical work that may still be outstanding: if
> `results.md`'s nDCG@10 table shows warning signs, the corresponding
> `python -m src.run_eval retrieval --retriever <r> --name <file>` re-runs have
> not finished; re-run them against the unchanged indexes (no re-indexing) and
> then `python -m scripts.render_results && python -m scripts.render_report`.
> Everything else on this page is kept as the historical build protocol.

You are a fresh headless agent. You do ONE high-value thing, verify it, commit it, and exit.
Progress lives on disk (this file, `PLAN.md`, `results.md`, git history) — never in context.

## Per-iteration protocol
1. Read `AUTOPILOT.md` (author's global loop rules, not part of this repo) (global rules), then this `LOOP.md`, then `PLAN.md` and the
   latest entries in `results.md`.
2. Confirm you are on branch `autopilot/work` (the runner guarantees this; if not, stop).
   NOTE: this branch was cut from `feat/cycle-5-visual-eval`, which has uncommitted changes in
   `src/run_eval.py` / `src/run_secondary.py` and an untracked `docs/adr/` — that IS in-progress
   cycle-5 work, not stray state. Review and properly finish/commit it first; do not discard it.
3. Pick the SINGLE highest-value open task: finishing cycle-5 (visual retrieval, ColQwen2 late
   interaction) code, then running its evaluation, then writing its verdict into `results.md`
   in the same style as cycles 0–4.
4. Do that one task. Small, reviewable diff. New logic ships with a test where applicable.
5. Run the gate: the eval task's gate is metrics actually written to `results.md` for that
   cycle — never estimated, never invented. Note: Qdrant runs in **embedded mode**
   (`QdrantClient(path=...)`), not as a separate service — there is nothing to start or check
   on a port for it. Ollama does run as a local service (`localhost:11434`) and generation
   depends on it — confirm it responds before any generation-dependent eval step.
6. On green: commit (Conventional Commits, English, imperative). Then exit.
7. If Ollama is not reachable, or a task needs a paid resource: log it clearly (as a blocker in
   your final report), commit only what is safe/complete, and stop rather than fabricate results.

## Project-specific hard constraints (never override)
- **Methodology integrity is the entire point of this project.** Never invent, estimate, or
  approximate an eval metric. Every number in `results.md` must come from an actual run.
- Never push to `origin` (GitHub remote exists) — local commits only; results land on
  `autopilot/work` for Nico to review before anything touches `main`.

## Gate (objective done-check)
Eval metrics actually written to `results.md` for the cycle in progress, from a real run.

## Where things are
- Plan / cycle status: `PLAN.md`
- Results / verdicts: `results.md`
- Corpus: `CORPUS.md`
