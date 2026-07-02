"""Unit tests for the results.md table-rendering script (scripts/render_results.py)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from render_results import fmt, render, render_metric_table, render_secondary_table, splice


class TestFmt:
    def test_rounds_to_two_decimals(self):
        assert fmt(0.6017) == "0.60"

    def test_none_renders_as_na(self):
        assert fmt(None) == "n/a"

    def test_bold_wraps_in_asterisks(self):
        assert fmt(0.72, bold=True) == "**0.72**"


class TestSplice:
    def test_replaces_content_between_populated_markers(self):
        content = "before\n<!-- auto:x:start -->\nold body\n<!-- auto:x:end -->\nafter"
        result = splice(content, "auto:x", "new body")
        assert result == "before\n<!-- auto:x:start -->\nnew body\n<!-- auto:x:end -->\nafter"

    def test_bootstraps_an_empty_marker_pair(self):
        content = "before\n<!-- auto:x:start -->\n<!-- auto:x:end -->\nafter"
        result = splice(content, "auto:x", "new body")
        assert "new body" in result
        assert result.count("<!-- auto:x:start -->") == 1

    def test_missing_marker_raises(self):
        with pytest.raises(ValueError):
            splice("no markers here", "auto:x", "body")

    def test_is_idempotent_on_repeated_calls(self):
        content = "<!-- auto:x:start -->\n<!-- auto:x:end -->"
        once = splice(content, "auto:x", "same body")
        twice = splice(once, "auto:x", "same body")
        assert once == twice


class TestRenderMetricTable:
    def test_always_show_all_renders_na_dash_for_closed_book(self):
        table = render_metric_table("recall@5", always_show_all=True)
        assert "| -1 | Closed book (no retrieval) | – | – | – | – | – |" in table

    def test_pending_cycle_renders_blank_cells_when_always_show_all(self):
        table = render_metric_table("recall@5", always_show_all=True)
        assert "| 6 | Agentic (optional) |  |  |  |  |  |" in table

    def test_skips_missing_cycles_when_not_always_show_all(self):
        table = render_metric_table("recall@10", always_show_all=False)
        assert "Closed book" not in table
        assert "Agentic" not in table

    def test_known_cycle_value_matches_source_json(self):
        table = render_metric_table("recall@5", always_show_all=False)
        data = json.loads((Path(__file__).resolve().parent.parent / "eval/results/cycle1_dense_retrieval.json").read_text())
        expected = f"{data['metrics']['global']['recall@5']:.2f}"
        line = next(line for line in table.splitlines() if line.startswith("| 1 |"))
        assert f"| {expected} |" in line


class TestRenderSecondaryTable:
    def test_closedbook_row_has_na_faithfulness(self):
        table = render_secondary_table()
        line = next(line for line in table.splitlines() if line.startswith("| -1 |"))
        assert "n/a (no context to be faithful to)" in line

    def test_cycle_without_secondary_file_is_skipped(self):
        table = render_secondary_table()
        assert not any(line.startswith("| 4 |") for line in table.splitlines())

    def test_manual_check_note_is_preserved(self):
        table = render_secondary_table()
        line = next(line for line in table.splitlines() if line.startswith("| 1 |"))
        assert "done (Claude, not human" in line


class TestRenderIsIdempotent:
    def test_rendering_twice_gives_identical_output(self):
        content = Path(__file__).resolve().parent.parent.joinpath("results.md").read_text(encoding="utf-8")
        once = render(content)
        twice = render(once)
        assert once == twice
