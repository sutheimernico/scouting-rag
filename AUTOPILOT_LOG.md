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

- 2026-07-02 — Ran the cycle-5 (visual) eval against the newly-built
  `data/visual_index.pt` (84 pages), on `autopilot/work` (88/88 tests
  green at start). Retrieval (59 golden-set queries) and generation (13
  visual-subset VLM answers) both actually ran — no estimated numbers.
  Found and root-caused a real bug: ColQwen2's language-model backbone
  loads with embed_tokens/norm weights randomly initialized instead of
  from the pretrained checkpoint (`colpali_engine==0.3.16` vs.
  `transformers==5.10.2` internal module-naming mismatch; confirmed by
  inspecting the loaded state dict directly, reproduced twice
  independently). This corrupts the index build and every query
  embedding — Recall@5 0.15 (2/13) is a real number but measures a broken
  model, not the retrieval technique. Separately, the intended `--k 5`
  generation run crashed immediately (`rag.py`'s `NUM_CTX=4096` sized for
  text, overflows at ~7,873 tokens for 5 images); used the
  already-supported `--k 1` flag instead for an honest end-to-end signal
  (number-hit 0.00, consistent with 0-of-13 correct top-1 retrievals).
  Wrote the full verdict into `results.md` (`1e3ec76`) and synced
  `PROJECT.md`'s cycle overview row (`47be2d3`). Gate: pytest green
  throughout (88/88), `scripts/render_results.py --check` clean. Needs
  Nico: sign off on a `colpali_engine`/`transformers` dependency fix
  before cycle 5 can be re-run for a real (not tooling-broken) verdict.
