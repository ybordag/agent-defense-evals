"""Dependency-free estimators used by the tail experiment suite."""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Mapping, Sequence


def _bounded(values: Iterable[float]) -> list[float]:
    materialized = list(values)
    if not materialized:
        raise ValueError("estimator requires at least one observation")
    if any(value < 0.0 or value > 1.0 for value in materialized):
        raise ValueError("loss observations must lie in [0, 1]")
    return materialized


def upper_tail_cvar(values: Iterable[float], tail_fraction: float) -> float:
    """Empirical upper-tail CVaR, with fractional boundary weighting."""

    losses = sorted(_bounded(values), reverse=True)
    if not 0.0 < tail_fraction <= 1.0:
        raise ValueError("tail_fraction must lie in (0, 1]")
    mass = len(losses) * tail_fraction
    full = int(math.floor(mass))
    fractional = mass - full
    total = sum(losses[:full])
    if fractional and full < len(losses):
        total += fractional * losses[full]
    return total / mass


def dkw_cvar_ucb(
    values: Iterable[float], tail_fraction: float, delta: float
) -> float:
    """Conservative CVaR UCB induced by the DKW CDF confidence band.

    For bounded losses, a CDF error epsilon changes an upper-tail average by
    at most epsilon / tail_fraction. Clipping preserves the [0, 1] support.
    """

    losses = _bounded(values)
    if not 0.0 < delta < 1.0:
        raise ValueError("delta must lie in (0, 1)")
    epsilon = math.sqrt(math.log(2.0 / delta) / (2.0 * len(losses)))
    return min(1.0, upper_tail_cvar(losses, tail_fraction) + epsilon / tail_fraction)


def wilson_upper(successes: int, trials: int, delta: float) -> float:
    """One-sided Wilson upper confidence bound for a Bernoulli probability."""

    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("invalid Bernoulli counts")
    if not 0.0 < delta < 1.0:
        raise ValueError("delta must lie in (0, 1)")
    z = statistics.NormalDist().inv_cdf(1.0 - delta)
    p = successes / trials
    denominator = 1.0 + z * z / trials
    center = p + z * z / (2.0 * trials)
    radius = z * math.sqrt(p * (1.0 - p) / trials + z * z / (4 * trials**2))
    return min(1.0, (center + radius) / denominator)


def hoeffding_difference_lower(
    paired_differences: Sequence[float], delta: float
) -> float:
    """Lower bound for the mean of paired differences in [-1, 1]."""

    if not paired_differences:
        raise ValueError("paired differences cannot be empty")
    if any(abs(item) > 1.0 for item in paired_differences):
        raise ValueError("paired differences must lie in [-1, 1]")
    radius = math.sqrt(2.0 * math.log(1.0 / delta) / len(paired_differences))
    return max(-1.0, statistics.fmean(paired_differences) - radius)


def spearman_correlation(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Spearman correlation with average ranks for ties."""

    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("Spearman correlation requires equal non-trivial samples")

    def ranks(values: Sequence[float]) -> list[float]:
        ordered = sorted(enumerate(values), key=lambda item: item[1])
        result = [0.0] * len(values)
        index = 0
        while index < len(ordered):
            end = index + 1
            while end < len(ordered) and ordered[end][1] == ordered[index][1]:
                end += 1
            rank = (index + end - 1) / 2.0 + 1.0
            for original, _ in ordered[index:end]:
                result[original] = rank
            index = end
        return result

    rx, ry = ranks(xs), ranks(ys)
    mean_x, mean_y = statistics.fmean(rx), statistics.fmean(ry)
    numerator = sum(
        (x - mean_x) * (y - mean_y) for x, y in zip(rx, ry, strict=True)
    )
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in rx)
        * sum((y - mean_y) ** 2 for y in ry)
    )
    return 0.0 if denominator == 0.0 else numerator / denominator


def maximum_cell_metric(metrics: Mapping[str, float]) -> float:
    if not metrics:
        raise ValueError("at least one cell metric is required")
    return max(metrics.values())
