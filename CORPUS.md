# Corpus Documentation

Acquired 2026-06-05. All raw data lives in `data/` (gitignored — see
licensing). Reproducibility: scraper/fetcher code in `scripts/` +
committed URL manifest `corpus_urls.jsonl` + fetch dates in the data files.

## Composition (three document classes)

| Class | Volume | Tokens (cl100k proxy) | Source |
|-------|--------|------------------------|--------|
| Prose articles | 283 docs, 394k words | 745,759 | Spielverlagerung.de (203), Miasanrot.de (80) |
| Stats tables | 7 CSVs | 209,592 (raw CSV) | OpenLigaDB 2025/26, worldfootballR/FBref 2024/25 |
| Visual stat sheets | 84 PNG pages | n/a (image) | self-rendered from the 2024/25 stats |
| **Total text** | | **955,351** | |

Token counts use tiktoken `cl100k_base` as a documented proxy (±10–15% vs.
the actual generator tokenizer). CSV tokens are raw-file counts; the
markdown chunk conversion (cycle 1) will differ somewhat.

## The long-context stop check (PLAN.md cycle 0)

**Is the corpus big enough that RAG is necessary?** Yes — twice over:

1. ~955k text tokens exceed every practical context window. Stuffing the
   corpus into a 1M-context API call would cost on the order of dollars
   *per query* and was ruled out anyway (local-only constraint, design D2).
2. On the local CPU-only setup the question answers itself: 7–8B models
   process prompts at a rate where even a 16k-token context takes minutes.
   Long-context is not an alternative here; retrieval is load-bearing.

**Not a stop candidate.**

## Sources, access checks, and licensing

### Used

- **Spielverlagerung.de** (DE) — 203 player portraits/analyses from the
  `spielerportrats/*` categories. robots.txt permits crawling (only
  `/wp-admin/` disallowed, no TDM opt-out found). Scraped with honest UA
  `ScoutingRAG-research/0.1`, ≥5s delay, fetch-once cache.
- **Miasanrot.de** (DE) — 80 newest posts (podcast posts excluded) via
  Yoast sitemap. robots.txt permits crawling. Same scraping rules.
- **OpenLigaDB** (api.openligadb.de) — open community API, no key, no
  rate-limit conflicts: final tables + top scorers, Bundesliga and
  2. Bundesliga 2025/26.
- **worldfootballR_data** (GitHub releases) — FBref extracts (.rds),
  filtered to Bundesliga 2024/25: shooting, passing, playing_time
  (the tables whose extracts cover that season completely).
- **Stat sheets** — rendered by us (`scripts/render_statsheets.py`) from
  the worldfootballR data; per-image ground truth in
  `data/statsheets/_manifest.jsonl`.

### Dropped after access checks (we do not work around access controls)

| Source | Reason |
|--------|--------|
| FBref direct | Cloudflare challenge (403) on stats pages |
| Understat | `robots.txt: Disallow: /` for all agents |
| Total Football Analysis | Cloudflare challenge already on robots.txt |
| abseits.at | robots.txt open, but Cloudflare challenge on content paths |

### Licensing posture

Article text is copyrighted; this corpus is for **private, non-commercial
research use only** (§ 44b/§ 53 UrhG posture): never committed, never
redistributed. Public repo artifacts contain at most short quotes
(golden-set ground-truth passages). Stats: OpenLigaDB is an open community
project; worldfootballR extracts derive from FBref — used privately, not
redistributed. Stat-sheet renderings are our own work derived from those
numbers, with source attribution in the image footer.

## Known skews and limitations (documented, accepted)

- **Two prose sources only**; Spielverlagerung dominates (72% of docs).
  Style diversity is limited accordingly.
- **Temporal split**: SV articles cluster 2011–2021 (Adventskalender
  short portraits + in-depth analyses), Miasanrot is entirely
  April–June 2026 (post-LLM-cutoff — deliberately valuable against
  parametric knowledge). Almost nothing in between (2024: 2 docs).
- **Miasanrot is FC-Bayern-centric**; SV portraits skew toward
  2012–2015-era players. Query construction was corpus-driven to match.
- **Stats season mix**: full-depth player metrics are 2024/25 (frozen
  extracts), freshness data (tables/scorers) is 2025/26. Stat sheets are
  2024/25. Documented per golden-set query.
- 3 extraction stubs (<100 words, index pages) remain in the corpus as
  realistic noise; median article is 1,152 words.
- OpenLigaDB scorer lists contain duplicate entries for the same player
  under name variants with separate counters (found in cycle 1: "F.
  Bilbija" 13 goals vs. "Bilbija"/"Filip Bilbija" 1 each). Kept as-is —
  realistic dirty data; golden-set keys reference the correct variant.
- Article length p90 is 2,177 words; max 11,962 (in-depth analyses).

## Article volume by year

2011–2015: 144 | 2016–2021: 57 | 2024: 2 | 2026: 80
