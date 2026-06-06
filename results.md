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

## Secondary: generation quality (judge-free number-hit + local judge)

Number-hit = all reference numbers appear in the answer (deterministic,
exact-match subset). Faithful (strict) = judge says every claim is
context-supported. Honest = supported OR honest refusal (the judge applied
the refusal rule inconsistently, so both readings are reported).

| Cycle | Number-hit exact-match (n=18) | Faithful strict (n=59) | Honest (n=59) | Refusal rate | Manual check (n=13) |
|-------|-------------------------------|------------------------|---------------|--------------|---------------------|
| −1 | **0.00** | n/a (no context to be faithful to) | n/a | – | – |
| 1 | **0.72** | 0.66 | 0.95 | 0.31 | pending (eval/FAITHFULNESS_SAMPLE.md) |

**Judge noise (test–retest, n=10, temp 0.3, seeds 1/2):** agreement 1.00 —
the judge is stable on this sample; n is small, treat as indicative.
Known judge weaknesses found in cycle 1: refusal flag inconsistent
(q001), one verdict contradicts a correct answer (q005), punishes honest
source complexity once (q036) — all flagged in the manual sample.

## Cost & latency per cycle

| Cycle | Indexing time (one-off) | Latency / query (CPU) | Extra infra | Notes |
|-------|-------------------------|------------------------|-------------|-------|
| −1 | – | ~48 s generation (measured under load, not representative) | Ollama | closed book |
| 1 | 106 min (BGE-M3 encode, 4,318 chunks) | 0.43 s retrieval + ~69 s generation (7B CPU) | Qdrant embedded | API cost: 0 €; judge run ~50 min one-off |

## Per-cycle deltas and verdicts

_One short block per cycle after its run: delta vs. previous stage,
interpretation, keep/drop decision. Honest: if a technique does not earn
its delta, it goes, and that gets documented here._

### Cycle 1 vs. cycle −1 (closed book)

- Number-hit on exact-match: **0.00 → 0.72**. Without retrieval the
  generator gets zero post-cutoff facts right (it refuses or treats
  2025/26 as future); with naive RAG it answers 13/18 correctly.
- Hallucination behavior: closed book invents player careers and
  strengths; with context the model almost never free-hallucinates
  (honest 0.95) — it errs toward over-cautious refusal instead.
- Retrieval R@5 0.60 global against a 0.72 text-cycle ceiling;
  semantic is saturated (1.00), the gaps are specific: season
  disambiguation (q013 answered with the wrong season's number),
  domain abbreviations (PPDA, q031), rank semantics not present in
  row chunks (q004), and a weak 7B generator that misses values inside
  long 30-column row chunks even when retrieval succeeded (q001, q011).
- **Verdict: keep.** This is the baseline every later cycle must beat;
  the exact-match and multi-hop gaps are exactly what cycles 2/3 target.
- Limitations: golden-set annotations machine-validated only (human 20%
  review skipped by owner decision, sample kept available); judge refusal
  flag unreliable; latency figures are CPU numbers.
