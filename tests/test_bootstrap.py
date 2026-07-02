"""Unit tests for the bootstrap CI helpers (src/bootstrap.py)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.bootstrap import bootstrap_mean_ci, paired_bootstrap_delta


class TestBootstrapMeanCi:
    def test_mean_matches_plain_average(self):
        result = bootstrap_mean_ci([1.0, 0.0, 1.0, 0.0], seed=1, n_resamples=2000)
        assert result["mean"] == pytest.approx(0.5)
        assert result["n"] == 4

    def test_ci_brackets_the_mean(self):
        result = bootstrap_mean_ci([0.2, 0.4, 0.6, 0.8, 1.0], seed=1, n_resamples=2000)
        assert result["ci_low"] <= result["mean"] <= result["ci_high"]

    def test_constant_values_give_a_degenerate_ci(self):
        result = bootstrap_mean_ci([0.7] * 10, seed=1, n_resamples=2000)
        assert result["ci_low"] == pytest.approx(0.7)
        assert result["ci_high"] == pytest.approx(0.7)

    def test_same_seed_is_reproducible(self):
        values = [0.1, 0.9, 0.3, 0.7, 0.5, 0.2]
        a = bootstrap_mean_ci(values, seed=42, n_resamples=1000)
        b = bootstrap_mean_ci(values, seed=42, n_resamples=1000)
        assert a == b

    def test_different_seeds_can_differ(self):
        values = [0.1, 0.9, 0.3, 0.7, 0.5, 0.2]
        a = bootstrap_mean_ci(values, seed=1, n_resamples=1000)
        b = bootstrap_mean_ci(values, seed=2, n_resamples=1000)
        assert a["ci_low"] != b["ci_low"] or a["ci_high"] != b["ci_high"]

    def test_empty_values_raises(self):
        with pytest.raises(ValueError):
            bootstrap_mean_ci([])


class TestPairedBootstrapDelta:
    def test_uniform_positive_delta_excludes_zero(self):
        a = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        b = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        result = paired_bootstrap_delta(a, b, seed=1, n_resamples=2000)
        assert result["mean"] == pytest.approx(1.0)
        assert result["excludes_zero"] is True

    def test_no_delta_does_not_exclude_zero(self):
        a = [0.3, 0.5, 0.7, 0.9]
        result = paired_bootstrap_delta(a, a, seed=1, n_resamples=2000)
        assert result["mean"] == pytest.approx(0.0)
        assert result["excludes_zero"] is False

    def test_mismatched_lengths_raise(self):
        with pytest.raises(ValueError):
            paired_bootstrap_delta([1.0, 2.0], [1.0])

    def test_noisy_small_delta_does_not_falsely_exclude_zero(self):
        # small, noisy sample where the true effect is ~0 with wide spread —
        # CI should be wide enough to include zero, not overclaim significance.
        a = [0.2, 0.8, 0.4, 0.9, 0.1, 0.6, 0.3, 0.7]
        b = [0.3, 0.7, 0.5, 0.8, 0.2, 0.5, 0.4, 0.6]
        result = paired_bootstrap_delta(a, b, seed=1, n_resamples=5000)
        assert result["excludes_zero"] is False
