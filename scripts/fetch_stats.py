#!/usr/bin/env python3
"""Fetch the stats-table corpus class (design spec, section 1b).

Sources after access checks (documented in CORPUS.md):

- OpenLigaDB (open community API, no key required): season 2025/26 final
  league tables and top-scorer lists for Bundesliga (bl1) and 2. Bundesliga
  (bl2). Provides post-cutoff freshness (mitigation M3).
- worldfootballR_data GitHub releases (FBref extracts, .rds): full-depth
  player season stats for 2024/25 (shooting, passing, playing_time — the
  tables whose extracts cover that season completely), filtered to the
  Bundesliga. Basis for stat-sheet rendering; prior-season status is a
  documented limitation.

Dropped sources: FBref direct (Cloudflare challenge), Understat (robots.txt
Disallow: /). We do not work around access controls.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyreadr
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
STATS_DIR = REPO_ROOT / "data" / "stats"

USER_AGENT = "ScoutingRAG-research/0.1 (private research project)"
DELAY_S = 2.0

OPENLIGADB = "https://api.openligadb.de"
# (league code, season start year, output label)
OPENLIGA_SETS = [
    ("bl1", "2025", "bundesliga"),
    ("bl2", "2025", "2_bundesliga"),
]

WFR_BASE = (
    "https://github.com/JaseZiv/worldfootballR_data/releases/download/"
    "fb_big5_advanced_season_stats"
)
# tables whose extracts were refreshed 2025-09 and therefore contain the
# complete 2024/25 season (defense/possession/misc are frozen at 2024-10)
WFR_TABLES = ["shooting", "passing", "playing_time"]
WFR_SEASON_END = 2025  # FBref convention: season end year, 2025 = 2024/25


def filter_bundesliga(df: pd.DataFrame, season_end_year: int) -> pd.DataFrame:
    """Bundesliga rows of one season from a worldfootballR big5 frame.

    big5 frames only contain the five top leagues, so a 'Bundesliga'
    substring match cannot collide with 2. Bundesliga.
    """
    comp_col = "Comp" if "Comp" in df.columns else "comp"
    season_col = "Season_End_Year" if "Season_End_Year" in df.columns else "season_end_year"
    mask = df[comp_col].str.contains("Bundesliga", na=False) & (df[season_col] == season_end_year)
    return df[mask].reset_index(drop=True)


def fetch_openligadb(session: requests.Session) -> list[dict]:
    out_dir = STATS_DIR / "openligadb"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = []
    for league, season, label in OPENLIGA_SETS:
        for endpoint, name in [("getbltable", "table"), ("getgoalgetters", "scorers")]:
            url = f"{OPENLIGADB}/{endpoint}/{league}/{season}"
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
            df = pd.DataFrame(resp.json())
            path = out_dir / f"{label}_{season}_{name}.csv"
            df.to_csv(path, index=False)
            meta.append({"url": url, "rows": len(df), "file": path.name})
            print(f"  {path.name}: {len(df)} rows")
            time.sleep(DELAY_S)
    return meta


def fetch_worldfootballr(session: requests.Session) -> list[dict]:
    out_dir = STATS_DIR / "fbref_wfr"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = []
    for table in WFR_TABLES:
        url = f"{WFR_BASE}/big5_player_{table}.rds"
        rds_path = out_dir / f"big5_player_{table}.rds"
        if not rds_path.exists():  # fetch once, cache
            resp = session.get(url, timeout=180)
            resp.raise_for_status()
            rds_path.write_bytes(resp.content)
            time.sleep(DELAY_S)
        frames = pyreadr.read_r(str(rds_path))
        df = next(iter(frames.values()))
        filtered = filter_bundesliga(df, WFR_SEASON_END)
        path = out_dir / f"bundesliga_2425_{table}.csv"
        filtered.to_csv(path, index=False)
        meta.append(
            {
                "url": url,
                "rows_total": len(df),
                "rows_bundesliga_2425": len(filtered),
                "file": path.name,
            }
        )
        print(f"  {path.name}: {len(filtered)} rows (of {len(df)} in extract)")
    return meta


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "openligadb": fetch_openligadb(session),
        "worldfootballr": fetch_worldfootballr(session),
    }
    (STATS_DIR / "_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"meta written -> {STATS_DIR / '_meta.json'}")


if __name__ == "__main__":
    main()
