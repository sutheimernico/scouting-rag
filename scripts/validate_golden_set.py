#!/usr/bin/env python3
"""Validate the golden set against the actual corpus files.

Checks (exit code 1 on any failure):
- JSONL parses; ids unique; types are known; subset sizes reported
- every ground-truth doc_id exists under data/
- kind=passage: quote is a verbatim substring of the article text
  (after whitespace normalization, per eval/SCHEMA.md)
- kind=table_row: every match_key occurs in the CSV; numeric keys must
  occur as a whole word somewhere in the file
- kind=image: the PNG exists and is listed in the statsheet manifest
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / "data"
GOLDEN = REPO_ROOT / "eval" / "golden_set.jsonl"

KNOWN_TYPES = {"semantic", "exact_match", "multi_hop", "visual"}


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def check_passage(entry_id: str, gt: dict, errors: list[str]) -> None:
    path = DATA / gt["doc_id"]
    if not path.exists():
        errors.append(f"{entry_id}: missing doc {gt['doc_id']}")
        return
    doc = json.loads(path.read_text(encoding="utf-8"))
    if norm_ws(gt["quote"]) not in norm_ws(doc.get("text") or ""):
        errors.append(f"{entry_id}: quote not found in {gt['doc_id']}: {gt['quote'][:60]!r}...")


def _key_in(key: str, text: str) -> bool:
    if re.fullmatch(r"[\d.,]+", key):
        return re.search(rf"(?<![\d.]){re.escape(key)}(?![\d.])", text) is not None
    return key in text


def check_table_row(entry_id: str, gt: dict, errors: list[str]) -> None:
    """All match_keys must co-occur in a single CSV line — this mirrors the
    later chunk semantics (one table row -> one chunk) and prevents
    file-wide false positives."""
    path = DATA / gt["doc_id"]
    if not path.exists():
        errors.append(f"{entry_id}: missing doc {gt['doc_id']}")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if not any(all(_key_in(k, line) for k in gt["match_keys"]) for line in lines):
        errors.append(f"{entry_id}: keys {gt['match_keys']} not co-located in any row of {gt['doc_id']}")


def check_image(entry_id: str, gt: dict, errors: list[str], manifest_files: set[str]) -> None:
    path = DATA / gt["doc_id"]
    if not path.exists():
        errors.append(f"{entry_id}: missing image {gt['doc_id']}")
    elif Path(gt["doc_id"]).name not in manifest_files:
        errors.append(f"{entry_id}: image {gt['doc_id']} not in statsheet manifest")


def main() -> None:
    manifest_files = set()
    manifest_path = DATA / "statsheets" / "_manifest.jsonl"
    if manifest_path.exists():
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            manifest_files.add(json.loads(line)["file"])

    errors: list[str] = []
    ids: list[str] = []
    types: Counter = Counter()

    for n, line in enumerate(GOLDEN.read_text(encoding="utf-8").splitlines(), 1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {n}: invalid JSON ({exc})")
            continue
        ids.append(entry["id"])
        if entry["type"] not in KNOWN_TYPES:
            errors.append(f"{entry['id']}: unknown type {entry['type']!r}")
        types[entry["type"]] += 1
        for gt in entry["ground_truth"]:
            if gt["kind"] == "passage":
                check_passage(entry["id"], gt, errors)
            elif gt["kind"] == "table_row":
                check_table_row(entry["id"], gt, errors)
            elif gt["kind"] == "image":
                check_image(entry["id"], gt, errors, manifest_files)
            else:
                errors.append(f"{entry['id']}: unknown kind {gt['kind']!r}")

    dupes = [i for i, c in Counter(ids).items() if c > 1]
    if dupes:
        errors.append(f"duplicate ids: {dupes}")

    print(f"{len(ids)} queries | per type: {dict(types)}")
    if errors:
        print(f"\n{len(errors)} VALIDATION ERRORS:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print("all ground-truth references verified against the corpus ✓")


if __name__ == "__main__":
    main()
