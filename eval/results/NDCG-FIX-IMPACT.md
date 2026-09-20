# Impact of the deduplicated nDCG fix (2026-09-20)

The nDCG@10 implementation counted duplicate ground-truth hits, which could push the score above
1.0. The fix (`eval_metrics_version: 2026-09-20-ndcg-dedup`) deduplicates coverage before scoring.
Every cycle was rescored from the stored run artefacts — no re-indexing, no new retrieval.

## What moved

| Configuration | before | after | delta |
|---|---:|---:|---:|
| cycle1 dense | 0.5340 | 0.5340 | 0.0000 |
| cycle2 hybrid | 0.5224 | 0.5224 | 0.0000 |
| cycle3 dense + rerank | 0.6507 | 0.6157 | −0.0350 |
| cycle3 hybrid + rerank | 0.6486 | 0.6149 | −0.0337 |
| cycle4 dense + contextual + rerank | 0.6477 | 0.6178 | −0.0299 |
| cycle4 dense + contextual | 0.5345 | 0.5345 | 0.0000 |
| cycle5 visual | 0.0150 | 0.0272 | +0.0122 |

Only the reranked configurations move, which is what the review predicted: reranking is exactly
what promotes several chunks of the same source document into the top 10, and those duplicates
were the ones being double-counted.

## Does it overturn a verdict?

**"Reranking is the recommended stack" — unchanged and, if anything, cleaner.** Reranking still
adds +0.08 nDCG@10 over plain dense retrieval (0.5340 → 0.6157). The gain shrank by a third
because part of it was the artefact, but it survives comfortably.

**"Contextual is a drop" — the verdict stands, the stated reason does not.** The comparison that
matters is dense+rerank against dense+contextual+rerank:

- before the fix: 0.6507 vs 0.6477 → contextual looked **worse** by 0.0030
- after the fix: 0.6157 vs 0.6178 → contextual looks **better** by 0.0021

The sign flipped. Both magnitudes are far below anything this golden set can resolve, so the
honest reading is not "contextual helps after all" — it is **"contextual makes no measurable
difference in either direction"**. Dropping it remains the right call, because it costs indexing
time and buys nothing measurable. But the earlier write-up justified the drop with a measured
disadvantage that was an artefact of the bug. That sentence has to change.

**Cycle 5 (visual) stays inconclusive.** 0.0150 → 0.0272 is a near-doubling of a number that is
still an order of magnitude below every text configuration, and it rests on the ColQwen2 run that
the dependency bug already made unreliable.

## Consequence for the final synthesis

The synthesis mandated in `PLAN.md` §5 must state the contextual result as *not distinguishable
from zero*, not as *worse*. The ranking at the top of the table (three configurations within
0.003 of each other) must not be presented as an ordering at all.
