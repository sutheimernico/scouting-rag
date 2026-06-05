"""Unit tests for the pure data logic of render_statsheets (no rendering)."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from render_statsheets import (
    METRICS,
    add_percentiles,
    build_metrics,
    parse_age,
    position_group,
    select_players,
    slugify,
)


def _extracts():
    base = {
        "Player": ["Star Striker", "Bench Kid", "Deep Playmaker"],
        "Squad": ["FC Test", "FC Test", "SV Probe"],
        "Pos": ["FW", "FW,MF", "MF"],
        "Age": ["24-100", "18", "31"],
        "Mins_Per_90": [30.0, 2.0, 28.0],
    }
    shooting = pd.DataFrame(
        {
            **base,
            "Gls_Standard": [24, 1, 3],
            "Sh_per_90_Standard": [3.5, 1.0, 1.2],
            "SoT_percent_Standard": [48.0, 20.0, 35.0],
            "npxG_Expected": [21.0, 0.5, 2.5],
        }
    )
    passing = pd.DataFrame(
        {
            **base,
            "xAG": [6.0, 0.2, 8.0],
            "KP": [40, 2, 70],
            "PrgP": [90, 5, 200],
            "Cmp_percent_Total": [78.0, 70.0, 88.0],
        }
    )
    playing = pd.DataFrame({**base, "Min_Playing.Time": [2700, 180, 2520]})
    return shooting, passing, playing


def test_build_metrics_joins_filters_minutes_and_derives_per90():
    df = build_metrics(*_extracts())
    # Bench Kid (180 min) is dropped by the MIN_MINUTES filter
    assert sorted(df["player"]) == ["Deep Playmaker", "Star Striker"]
    striker = df[df["player"] == "Star Striker"].iloc[0]
    assert striker["goals_per90"] == 24 / 30.0
    assert striker["pos_group"] == "FW"


def test_position_group_takes_first_position_and_drops_gk():
    assert position_group("FW,MF") == "FW"
    assert position_group("GK") is None


def test_parse_age_handles_years_days_format():
    assert parse_age("24-100") == 24.0
    assert parse_age(None) is None


def test_add_percentiles_within_group_bounds():
    df = add_percentiles(build_metrics(*_extracts()))
    for key, _ in METRICS:
        col = df[f"{key}_pct"]
        assert col.between(0, 100).all()
    # sole member of its group sits at the 100th percentile
    playmaker = df[df["player"] == "Deep Playmaker"].iloc[0]
    assert playmaker["kp_per90_pct"] == 100


def test_select_players_caps_per_group():
    df = add_percentiles(build_metrics(*_extracts()))
    assert len(select_players(df, per_group=1)) == 2  # one FW + one MF


def test_slugify_is_ascii_and_stable():
    assert slugify("Léon Müller-Ñ") == "leon_muller_n"
