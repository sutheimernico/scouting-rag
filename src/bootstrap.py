"""Bootstrap confidence intervals over existing per-query eval results.

No new eval runs needed: every function here resamples query-level values
that are already stored in eval/results/*.json ("details" arrays). Used to
harden the point estimates in results.md (n=13-59 per subset is small
enough that a single query can move a metric by several points — PLAN.md's
"deutet auf, nicht beweist" principle) with an explicit interval instead of
a bare mean.

Percentile bootstrap, fixed seed for reproducibility (PLAN.md iron
principle: reproducible, fixed seed where possible).
"""

from __future__ import annotations

import numpy as np

DEFAULT_SEED = 1234
DEFAULT_RESAMPLES = 10_000


def bootstrap_mean_ci(
    values: list[float],
    seed: int = DEFAULT_SEED,
    n_resamples: int = DEFAULT_RESAMPLES,
    alpha: float = 0.05,
) -> dict:
    """Percentile bootstrap CI for the mean of `values`.

    Returns {"n", "mean", "ci_low", "ci_high", "alpha"}.
    """
    if not values:
        raise ValueError("bootstrap_mean_ci requires at least one value")
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))
    resample_means = arr[idx].mean(axis=1)
    lo, hi = np.percentile(resample_means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {
        "n": n,
        "mean": round(float(arr.mean()), 4),
        "ci_low": round(float(lo), 4),
        "ci_high": round(float(hi), 4),
        "alpha": alpha,
    }


def paired_bootstrap_delta(
    values_a: list[float],
    values_b: list[float],
    seed: int = DEFAULT_SEED,
    n_resamples: int = DEFAULT_RESAMPLES,
    alpha: float = 0.05,
) -> dict:
    """Paired bootstrap CI for the mean delta (b - a) over matched queries.

    `values_a[i]` and `values_b[i]` must be the same query, e.g. cycle-A and
    cycle-B metric values aligned by golden-set id. Resampling query indices
    (not the deltas independently) preserves the pairing.

    Returns bootstrap_mean_ci's fields plus "excludes_zero" — the honest
    significance hint: the CI does not cross zero. This is a description of
    the interval, not a p-value; report it as "deutet auf", not "beweist"
    at this n.
    """
    if len(values_a) != len(values_b):
        raise ValueError("paired arrays must have equal length")
    deltas = [b - a for a, b in zip(values_a, values_b)]
    result = bootstrap_mean_ci(deltas, seed=seed, n_resamples=n_resamples, alpha=alpha)
    result["excludes_zero"] = bool(result["ci_low"] > 0 or result["ci_high"] < 0)
    return result
