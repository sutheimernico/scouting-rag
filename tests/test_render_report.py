"""Unit tests for the static HTML report generator (scripts/render_report.py)."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from render_report import CYCLE5_SECTION, build_html, grouped_bar_chart, render_table, svg_escape


class TestSvgEscape:
    def test_escapes_html_special_characters(self):
        assert svg_escape('a < b & "c" > d') == "a &lt; b &amp; &quot;c&quot; &gt; d"


class TestGroupedBarChart:
    def test_bar_height_is_proportional_to_value(self):
        svg = grouped_bar_chart(["c1"], {"s1": [1.0]}, {"s1": "#fff"}, y_max=1.0, height=200)
        rect_heights = [float(h) for h in re.findall(r'<rect[^>]*height="([\d.]+)"', svg)]
        # the full-value (1.0 of y_max=1.0) bar should span almost the whole plot height
        assert len(rect_heights) == 1
        assert rect_heights[0] > 150

    def test_none_values_are_skipped_without_crashing(self):
        svg = grouped_bar_chart(["c1", "c2"], {"s1": [0.5, None]}, {"s1": "#fff"})
        assert "<svg" in svg

    def test_no_negative_dimensions(self):
        svg = grouped_bar_chart(["a", "b", "c"], {"x": [0.1, 0.9, 0.5], "y": [1.0, 0.0, 0.3]}, {"x": "#111", "y": "#222"})
        for w in re.findall(r'width="([\-\d.]+)"', svg):
            assert float(w) >= 0
        for h in re.findall(r'height="([\-\d.]+)"', svg):
            assert float(h) >= 0

    def test_zero_value_renders_no_visible_bar_but_no_crash(self):
        svg = grouped_bar_chart(["c1"], {"s1": [0.0]}, {"s1": "#fff"})
        assert "<svg" in svg


class TestRenderTable:
    def test_renders_header_and_rows(self):
        html = render_table(["A", "B"], [["1", "2"], ["3", "4"]])
        assert "<th>A</th>" in html
        assert "<td>3</td>" in html


class TestBuildHtml:
    def test_no_external_resources(self):
        html = build_html(CYCLE5_SECTION)
        assert "http://" not in html
        assert "https://" not in html
        assert "<script src" not in html
        assert '<link ' not in html

    def test_has_no_javascript(self):
        html = build_html(CYCLE5_SECTION)
        assert "<script" not in html

    def test_contains_title_and_cycle5_section(self):
        html = build_html(CYCLE5_SECTION)
        assert "<title>" in html
        assert "Cycle 5: Visual retrieval" in html

    def test_is_deterministic(self):
        assert build_html(CYCLE5_SECTION) == build_html(CYCLE5_SECTION)
