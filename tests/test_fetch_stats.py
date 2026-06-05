"""Unit tests for the pure filtering logic of fetch_stats (no network)."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from fetch_stats import filter_bundesliga


def _frame(comp_col: str, season_col: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            comp_col: ["Bundesliga", "La Liga", "Bundesliga", "Premier League"],
            season_col: [2025, 2025, 2024, 2025],
            "Player": ["A", "B", "C", "D"],
        }
    )


def test_filter_bundesliga_keeps_only_matching_league_and_season():
    out = filter_bundesliga(_frame("Comp", "Season_End_Year"), 2025)
    assert list(out["Player"]) == ["A"]


def test_filter_bundesliga_handles_lowercase_columns():
    out = filter_bundesliga(_frame("comp", "season_end_year"), 2024)
    assert list(out["Player"]) == ["C"]


def test_filter_bundesliga_ignores_nan_comp():
    df = _frame("Comp", "Season_End_Year")
    df.loc[1, "Comp"] = None
    out = filter_bundesliga(df, 2025)
    assert list(out["Player"]) == ["A"]
