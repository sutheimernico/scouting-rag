#!/usr/bin/env python3
"""Render the visual corpus class: per-player pizza stat sheets (design spec 1c).

Input: worldfootballR 2024/25 Bundesliga extracts (shooting, passing,
playing_time). Output: one PNG pizza chart per selected player plus a
ground-truth manifest (_manifest.jsonl) that records the exact raw and
percentile values encoded in every image — the basis for the visual
golden-set queries.

Percentiles are computed within position groups (DF/MF/FW, GK excluded)
over all players with >= MIN_MINUTES. Selection is balanced: top players
by minutes per position group.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd
from mplsoccer import PyPizza

REPO_ROOT = Path(__file__).resolve().parent.parent
STATS_DIR = REPO_ROOT / "data" / "stats" / "fbref_wfr"
OUT_DIR = REPO_ROOT / "data" / "statsheets"
MANIFEST = OUT_DIR / "_manifest.jsonl"

SEASON_LABEL = "2024/25"
MIN_MINUTES = 900
PER_GROUP = 28  # 3 position groups -> 84 sheets (target band: 60-100)

# metric key -> axis label on the pizza
METRICS: list[tuple[str, str]] = [
    ("npxg_per90", "npxG /90"),
    ("shots_per90", "Shots /90"),
    ("sot_pct", "SoT %"),
    ("goals_per90", "Goals /90"),
    ("xag_per90", "xAG /90"),
    ("kp_per90", "Key passes /90"),
    ("prgp_per90", "Prog. passes /90"),
    ("pass_cmp_pct", "Pass cmp %"),
]


def parse_age(value) -> float | None:
    """FBref ages come as '24' or '24-123' (years-days)."""
    try:
        return float(str(value).split("-")[0])
    except (TypeError, ValueError):
        return None


def position_group(pos) -> str | None:
    """First listed position; GK and unknowns are excluded (no keeper metrics)."""
    first = str(pos).split(",")[0].strip()
    return first if first in {"DF", "MF", "FW"} else None


def build_metrics(shooting: pd.DataFrame, passing: pd.DataFrame, playing: pd.DataFrame) -> pd.DataFrame:
    """Join the three extracts and derive the pizza metrics per player."""
    keys = ["Player", "Squad"]
    df = shooting.merge(passing, on=keys, suffixes=("", "_pass"), how="inner")
    df = df.merge(playing, on=keys, suffixes=("", "_time"), how="inner")
    df = df.drop_duplicates(subset=keys)

    nineties = df["Mins_Per_90"]  # FBref '90s': minutes / 90
    out = pd.DataFrame(
        {
            "player": df["Player"],
            "squad": df["Squad"],
            "pos_group": df["Pos"].map(position_group),
            "age": df["Age"].map(parse_age),
            "minutes": df["Min_Playing.Time"],
            "npxg_per90": df["npxG_Expected"] / nineties,
            "shots_per90": df["Sh_per_90_Standard"],
            "sot_pct": df["SoT_percent_Standard"],
            "goals_per90": df["Gls_Standard"] / nineties,
            "xag_per90": df["xAG"] / nineties,
            "kp_per90": df["KP"] / nineties,
            "prgp_per90": df["PrgP"] / nineties,
            "pass_cmp_pct": df["Cmp_percent_Total"],
        }
    )
    out = out[out["pos_group"].notna() & (out["minutes"] >= MIN_MINUTES)]
    return out.reset_index(drop=True)


def add_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    """Percentile (0-100) of every metric within its position group."""
    df = df.copy()
    for key, _label in METRICS:
        df[f"{key}_pct"] = (
            df.groupby("pos_group")[key].rank(pct=True, na_option="bottom") * 100
        ).round(0)
    return df


def select_players(df: pd.DataFrame, per_group: int = PER_GROUP) -> pd.DataFrame:
    """Balanced selection: top players by minutes within each position group."""
    return (
        df.sort_values("minutes", ascending=False)
        .groupby("pos_group")
        .head(per_group)
        .reset_index(drop=True)
    )


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")


def render_sheet(row: pd.Series, out_path: Path) -> None:
    values = [int(row[f"{key}_pct"]) for key, _ in METRICS]
    pizza = PyPizza(
        params=[label for _, label in METRICS],
        straight_line_color="#222222",
        straight_line_lw=1,
        last_circle_lw=1,
        other_circle_lw=0,
    )
    fig, _ax = pizza.make_pizza(
        values,
        figsize=(8, 8.6),
        color_blank_space="same",
        kwargs_slices=dict(facecolor="#1f77b4", edgecolor="#222222", linewidth=1),
        kwargs_params=dict(color="#222222", fontsize=11),
        kwargs_values=dict(
            color="#ffffff",
            fontsize=11,
            bbox=dict(facecolor="#1f77b4", edgecolor="#222222", boxstyle="round,pad=0.2"),
        ),
    )
    age = f"{int(row['age'])}" if pd.notna(row["age"]) else "?"
    fig.text(
        0.5, 0.97,
        f"{row['player']} — {row['squad']}",
        ha="center", fontsize=15, fontweight="bold",
    )
    fig.text(
        0.5, 0.94,
        f"{row['pos_group']} | age {age} | {int(row['minutes'])} min | "
        f"Bundesliga {SEASON_LABEL} | percentiles vs. {row['pos_group']}",
        ha="center", fontsize=10, color="#444444",
    )
    fig.text(
        0.5, 0.02,
        "Data: FBref via worldfootballR extracts | rendered by scouting-rag",
        ha="center", fontsize=7, color="#888888",
    )
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    import matplotlib.pyplot as plt

    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shooting = pd.read_csv(STATS_DIR / "bundesliga_2425_shooting.csv")
    passing = pd.read_csv(STATS_DIR / "bundesliga_2425_passing.csv")
    playing = pd.read_csv(STATS_DIR / "bundesliga_2425_playing_time.csv")

    metrics = add_percentiles(build_metrics(shooting, passing, playing))
    selected = select_players(metrics)
    print(f"rendering {len(selected)} sheets "
          f"({selected.groupby('pos_group').size().to_dict()})")

    with MANIFEST.open("w", encoding="utf-8") as manifest:
        for _, row in selected.iterrows():
            filename = f"{slugify(row['player'])}_{slugify(row['squad'])}.png"
            render_sheet(row, OUT_DIR / filename)
            manifest.write(
                json.dumps(
                    {
                        "file": filename,
                        "player": row["player"],
                        "squad": row["squad"],
                        "pos_group": row["pos_group"],
                        "age": row["age"],
                        "minutes": int(row["minutes"]),
                        "season": SEASON_LABEL,
                        "metrics": {
                            key: {
                                "label": label,
                                "raw": round(float(row[key]), 3),
                                "percentile": int(row[f"{key}_pct"]),
                            }
                            for key, label in METRICS
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"done -> {OUT_DIR} (+ {MANIFEST.name})")


if __name__ == "__main__":
    main()
