#!/usr/bin/env python3
"""Generate the human review sample for golden-set annotations.

Draws a seeded, type-stratified ~20% sample and writes
eval/REVIEW_SAMPLE.md with everything needed to verify each annotation
without opening raw files: the query, my annotation, and the evidence
(quote in context / actual CSV row / manifest values for images).
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / "data"
GOLDEN = REPO_ROOT / "eval" / "golden_set.jsonl"
OUT = REPO_ROOT / "eval" / "REVIEW_SAMPLE.md"

# per-type sample counts (~20% of 18/15/13/13)
SAMPLE_PLAN = {"exact_match": 4, "semantic": 3, "multi_hop": 3, "visual": 2}


def quote_in_context(doc_id: str, quote: str, margin: int = 160) -> tuple[str, str]:
    doc = json.loads((DATA / doc_id).read_text(encoding="utf-8"))
    text = doc.get("text") or ""
    norm = re.sub(r"\s+", " ", text)
    qnorm = re.sub(r"\s+", " ", quote)
    pos = norm.find(qnorm)
    if pos < 0:
        return doc.get("title") or doc_id, f"(quote not found?) {quote}"
    start, end = max(0, pos - margin), min(len(norm), pos + len(qnorm) + margin)
    ctx = norm[start:end]
    ctx = ctx.replace(qnorm, f"**{qnorm}**")
    return doc.get("title") or doc_id, ("…" if start else "") + ctx + ("…" if end < len(norm) else "")


def csv_rows(doc_id: str, match_keys: list[str]) -> list[str]:
    def key_in(key: str, line: str) -> bool:
        if re.fullmatch(r"[\d.,]+", key):
            return re.search(rf"(?<![\d.]){re.escape(key)}(?![\d.])", line) is not None
        return key in line

    lines = (DATA / doc_id).read_text(encoding="utf-8").splitlines()
    return [l[:220] for l in lines if all(key_in(k, l) for k in match_keys)]


def manifest_entry(doc_id: str) -> dict | None:
    fname = Path(doc_id).name
    for line in (DATA / "statsheets" / "_manifest.jsonl").read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        if entry["file"] == fname:
            return entry
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    by_type = defaultdict(list)
    for line in GOLDEN.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        by_type[entry["type"]].append(entry)

    rng = random.Random(args.seed)
    sample = []
    for qtype, count in SAMPLE_PLAN.items():
        sample.extend(rng.sample(by_type[qtype], count))
    sample.sort(key=lambda e: e["id"])

    out = [
        f"# Golden-Set Review Sample (20%, seed={args.seed})",
        "",
        "Für jede Query unten: Prüfe, ob der gezeigte Beleg die Frage wirklich",
        "beantwortet und ob die Annotation (Quote/Zeile/Bild) die richtige Stelle",
        "markiert. Antworte pro Query mit ok oder nenne die q-Nummer + Problem.",
        "Statblätter liegen unter `data/statsheets/` (im Explorer/VS Code zu öffnen).",
        "",
    ]
    for entry in sample:
        out.append(f"## {entry['id']} ({entry['type']})")
        out.append("")
        out.append(f"**Query:** {entry['query']}")
        out.append(f"**Soll-Antwort:** {entry['reference_answer']}")
        out.append("")
        for gt in entry["ground_truth"]:
            if gt["kind"] == "passage":
                title, ctx = quote_in_context(gt["doc_id"], gt["quote"])
                out.append(f"- **Beleg (Artikel):** _{title}_ — `{gt['doc_id']}`")
                out.append(f"  > {ctx}")
            elif gt["kind"] == "table_row":
                rows = csv_rows(gt["doc_id"], gt["match_keys"])
                out.append(f"- **Beleg (Tabellenzeile):** `{gt['doc_id']}`, keys {gt['match_keys']}")
                for row in rows[:2]:
                    out.append(f"  > `{row}`")
            elif gt["kind"] == "image":
                m = manifest_entry(gt["doc_id"])
                out.append(f"- **Beleg (Statblatt):** `data/{gt['doc_id']}`")
                if m:
                    vals = ", ".join(f"{v['label']}: P{v['percentile']}" for v in m["metrics"].values())
                    out.append(f"  > Manifest: {m['player']} ({m['squad']}, {m['pos_group']}) — {vals}")
        out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {len(sample)} sample queries -> {OUT}")


if __name__ == "__main__":
    main()
