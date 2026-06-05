# Golden Set Schema (`golden_set.jsonl`)

One JSON object per line:

```json
{
  "id": "q001",
  "type": "semantic | exact_match | multi_hop | visual",
  "query": "German user query",
  "reference_answer": "short expected answer (for generation metrics)",
  "ground_truth": [
    {"doc_id": "articles/<id>.json", "kind": "passage", "quote": "verbatim substring of the document"},
    {"doc_id": "stats/openligadb/<file>.csv", "kind": "table_row", "match_keys": ["H. Kane", "36"]},
    {"doc_id": "statsheets/<file>.png", "kind": "image"}
  ],
  "notes": "optional curation notes"
}
```

## Conventions

- `doc_id` is the path relative to `data/`. Chunks produced in cycle 1+ must
  carry the `doc_id` of their source document so ground truth stays
  **chunking-agnostic** (PLAN.md cycles may change chunking; the golden set
  never has to change).
- Relevance rules for a retrieved chunk/page:
  - `passage`: chunk text contains `quote` as a substring after whitespace
    normalization.
  - `table_row`: chunk text contains **all** `match_keys`; purely numeric
    keys must match on word boundaries (so "36" does not match "136").
    Match keys use the **raw source-file representation** (fbref extracts
    store numerics as floats, e.g. "362.0"); the cycle-1 chunk conversion
    must preserve numeric representations from the source.
  - `image`: the retrieved page file equals `doc_id` (cycle 5); for text-only
    cycles, visual ground truth is unreachable by design — that gap **is**
    the measurement.
- Multi-entry ground truth (multi-hop): per-query recall = covered entries /
  all entries; a query counts as "hit" for MRR at the rank of the first
  covering chunk.
- Reference answers are for the secondary generation metrics only; primary
  metrics never look at them.

## Annotation process (documented limitation)

Queries are corpus-driven. Claude proposed queries and annotated ground
truth; Nico reviews a 20% sample before the cycle-0 report is accepted
("inter-rater light"). Stats-based values were extracted programmatically
from the source files, not typed from memory.
