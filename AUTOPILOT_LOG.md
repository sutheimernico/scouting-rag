# scouting-rag — autopilot iteration log

One line per iteration: date, what was done, gate result.

- 2026-07-02 — Portfolio-hardening pass on `autopilot/work` (46/46 tests green
  at start). (1) Added `PROJECT.md` steckbrief (`8e7ff44`). (2) Built
  `scripts/render_results.py` to auto-generate the primary/secondary metric
  tables in `results.md` from `eval/results/*.json` instead of manual
  transcription; regenerating surfaced and corrected drifted Precision@5
  numbers (cycles 2-4) and a pre-existing nDCG@10>1.0 metric bug (documented,
  not fixed — needs a full eval re-run and Nico's sign-off) (`0cb7d74`).
  (3) Added retrieval failure-rate (1-Recall@k) reporting, single-hop vs.
  multi-hop vs. visual (`e11d295`). (4) Added `src/bootstrap.py` (paired
  percentile bootstrap, fixed seed) and wired core cycle-comparison CIs into
  `results.md` (`4892203`). (5) Investigated cycle-5 (visual/ColQwen2):
  infra confirmed reachable (Ollama + qwen2.5vl:7b, ColQwen2 weights
  cached), but a timing smoke test measured 346-351s/page reproducibly on
  this CPU-only machine — extrapolates to ~8h index build / ~14-15h full
  eval, 16x the ~30min unattended-run budget. Not run; documented as
  Needs Nico with three options and exact commands (`6cca8f9`).
  (6) Added `scripts/render_report.py` generating a self-contained dark
  static HTML report (`report/index.html`) from the same eval JSONs — no
  build step, no JS, no external resources (`717bd2e`). Gate: pytest green
  throughout (46 → 88 tests), no new eval runs anywhere in this session.
  New dependency: none (numpy/scipy/beautifulsoup4 already pinned). Note:
  `PLAN.md` has no checkbox syntax (verbatim prose, "never silently
  edited" per its own header) — task tracking for this session lives here
  and in the commit history instead.
