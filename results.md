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

n per subset: semantic 15, exact-match 18, multi-hop 13, visual 13 (59 global).

**Effective recall ceilings in text-only cycles** (visual ground truth is
unreachable by design; 7 of 13 multi-hop queries have an image half):
global 0.72, multi-hop 0.73, visual 0.00. Read every text-cycle number
against these ceilings, not against 1.0.

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| −1 | Closed book (no retrieval) | – | – | – | – | – |
| 1 | Naive dense (BGE-M3) | 0.60 | **1.00** | 0.83 | 0.42 | 0.00 |
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
| 1 | Naive dense (BGE-M3) | 0.66 | 1.00 | 0.89 | 0.62 | 0.00 |

### Precision@5

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| 1 | Naive dense (BGE-M3) | 0.15 | 0.24 | 0.17 | 0.17 | 0.00 |

### MRR

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| 1 | Naive dense (BGE-M3) | 0.53 | 0.79 | 0.64 | 0.62 | 0.00 |

### nDCG@10

| Cycle | Technique | global | semantic | exact-match | multi-hop | visual |
|-------|-----------|--------|----------|-------------|-----------|--------|
| 1 | Naive dense (BGE-M3) | 0.56 | 0.95 | 0.70 | 0.49 | 0.00 |

## Secondary: generation quality (local judge + manual sample)

| Cycle | Faithfulness (judge) | Faithfulness (manual n=10) | Answer quality (judge) | Notes |
|-------|----------------------|----------------------------|------------------------|-------|
| −1 | | | | closed-book reference line |

**Judge noise (test–retest on 10 queries, measured once in cycle 1):** _pending_

## Cost & latency per cycle

| Cycle | Indexing time (one-off) | Latency / query (CPU) | Extra infra | Notes |
|-------|-------------------------|------------------------|-------------|-------|
| −1 | – | ~48 s generation (measured under load, not representative) | Ollama | closed book |
| 1 | 106 min (BGE-M3 encode, 4,318 chunks) | 0.43 s retrieval; generation TBD | Qdrant embedded | API cost: 0 € |

## Per-cycle deltas and verdicts

_One short block per cycle after its run: delta vs. previous stage,
interpretation, keep/drop decision. Honest: if a technique does not earn
its delta, it goes, and that gets documented here._
