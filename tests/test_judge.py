"""Unit tests for the deterministic part of the secondary metrics."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.judge import answer_number_hit, extract_numbers


def test_extract_numbers_handles_german_formats():
    assert extract_numbers("4.060 Minuten und 34,88 km/h") == ["4.060", "34,88"]


def test_hit_exact():
    assert answer_number_hit("Kane schoss 36 Tore.", "36 Tore.")


def test_hit_thousands_dot_variant():
    assert answer_number_hit("Er kam auf 4060 Minuten.", "4.060 Minuten.")


def test_hit_decimal_comma_variant():
    assert answer_number_hit("Top-Speed: 34.88 km/h", "34,88 km/h.")


def test_miss_wrong_number():
    assert not answer_number_hit("Kane schoss 26 Tore.", "36 Tore.")


def test_miss_refusal_answer():
    assert not answer_number_hit("Dazu finde ich nichts im Korpus.", "36 Tore.")


def test_all_reference_numbers_required():
    assert not answer_number_hit("70 Punkte.", "FC Schalke 04 mit 70 Punkten und 50 Toren.")


def test_hit_raw_float_form_matches_integer_reference():
    assert answer_number_hit("Er spielte 362.0 progressive Pässe.", "362 progressive Pässe.")
    assert answer_number_hit("26 Tore.", "26.0 Tore.")
