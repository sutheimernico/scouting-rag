# Results: Retrieval Technique Comparison

All numbers come from `eval/golden_set.jsonl` runs. Primary metrics are
judge-free IR metrics against hand-annotated ground-truth passages
(chunking-agnostic; a retrieved chunk is relevant iff it overlaps an
annotated passage). Secondary generation metrics use a local judge
(`llama3.1:8b`) and are reported with the measured judge noise. Latency
figures are honest CPU numbers (no GPU) and not production-representative.

State the sample size with every claim. With n≈12–15 per question type,
one query flips a metric by 7–8 points — phrase accordingly ("deutet auf",
not "beweist").

## Primary: Recall@5

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| −1 | Closed book (no retrieval) | – | – | – | – | – |
| 1 | Naive dense (BGE-M3) | | | | | |
| 2 | + Hybrid (sparse + RRF) | | | | | |
| 3 | + Reranking (cross-encoder) | | | | | |
| 4 | + Contextual retrieval | | | | | |
| 5 | Visual (ColQwen) | | | | | |
| 6 | Agentic (optional) | | | | | |

## Primary: Recall@10 / Precision@5 / MRR / nDCG@10

_Same table layout as Recall@5 — filled per cycle._

### Recall@10

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|

### Precision@5

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|

### MRR

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|

### nDCG@10

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|

## Secondary: generation quality (local judge + manual sample)

| Cycle | Faithfulness (judge) | Faithfulness (manual n=10) | Answer quality (judge) | Notes |
|-------|----------------------|----------------------------|------------------------|-------|
| −1 | | | | closed-book reference line |

**Judge noise (test–retest on 10 queries, measured once in cycle 1):** _pending_

## Cost & latency per cycle

| Cycle | Indexing time (one-off) | Latency / query (CPU) | Extra infra | Notes |
|-------|-------------------------|------------------------|-------------|-------|

## Per-cycle deltas and verdicts

_One short block per cycle after its run: delta vs. previous stage,
interpretation, keep/drop decision. Honest: if a technique does not earn
its delta, it goes, and that gets documented here._
