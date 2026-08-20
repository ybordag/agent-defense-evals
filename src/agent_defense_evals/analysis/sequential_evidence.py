"""Streaming monitors for anytime-valid and baseline evidence accumulation."""

import math
from collections.abc import Iterable
from typing import Protocol

from pydantic import Field

from agent_defense_evals.core.schemas import FrozenModel


class MonitorSnapshot(FrozenModel):
    step: int = Field(ge=0)
    statistic: float
    max_statistic: float
    alarm: bool


class MonitorRun(FrozenModel):
    alarm_step: int | None = Field(default=None, ge=0)
    terminal_statistic: float
    max_statistic: float


class StreamingMonitor(Protocol):
    monitor_id: str

    def update(self, score: float) -> MonitorSnapshot: ...


def _logsumexp(values: tuple[float, ...]) -> float:
    largest = max(values)
    if largest == -math.inf:
        return largest
    return largest + math.log(sum(math.exp(value - largest) for value in values))


class MixtureBettingEProcess:
    """Mixture of test martingales for scores with bounded conditional mean.

    For score Z_t in [0, 1] and E[Z_t | F_{t-1}] <= p0, every factor
    1 + lambda * (Z_t - p0) has conditional expectation at most one.
    A fixed mixture of their products is therefore an e-process.
    """

    monitor_id = "mixture_e_process"

    def __init__(
        self,
        *,
        null_mean_upper: float,
        alpha: float,
        bet_fractions: tuple[float, ...],
    ) -> None:
        if not 0.0 < null_mean_upper < 1.0:
            raise ValueError("null_mean_upper must be between zero and one")
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must be between zero and one")
        if not bet_fractions or any(
            fraction <= 0.0 or fraction >= 1.0 for fraction in bet_fractions
        ):
            raise ValueError("bet fractions must be nonempty and between zero and one")
        self._null_mean_upper = null_mean_upper
        self._log_threshold = math.log(1.0 / alpha)
        self._lambdas = tuple(
            fraction / null_mean_upper for fraction in bet_fractions
        )
        initial_weight = -math.log(len(self._lambdas))
        self._log_components = tuple(initial_weight for _ in self._lambdas)
        self._step = 0
        self._max_log_e = 0.0

    def update(self, score: float) -> MonitorSnapshot:
        if not 0.0 <= score <= 1.0:
            raise ValueError("e-process scores must lie in [0, 1]")
        updated = []
        for log_capital, betting_fraction in zip(
            self._log_components, self._lambdas, strict=True
        ):
            factor = 1.0 + betting_fraction * (
                score - self._null_mean_upper
            )
            updated.append(
                -math.inf if factor <= 0.0 else log_capital + math.log(factor)
            )
        self._log_components = tuple(updated)
        log_e = _logsumexp(self._log_components)
        self._max_log_e = max(self._max_log_e, log_e)
        snapshot = MonitorSnapshot(
            step=self._step,
            statistic=log_e,
            max_statistic=self._max_log_e,
            alarm=self._max_log_e >= self._log_threshold,
        )
        self._step += 1
        return snapshot


class FixedScoreThreshold:
    monitor_id = "fixed_per_turn"

    def __init__(self, threshold: float) -> None:
        self._threshold = threshold
        self._step = 0
        self._maximum = -math.inf

    def update(self, score: float) -> MonitorSnapshot:
        self._maximum = max(self._maximum, score)
        snapshot = MonitorSnapshot(
            step=self._step,
            statistic=score,
            max_statistic=self._maximum,
            alarm=score > self._threshold,
        )
        self._step += 1
        return snapshot


class PageCusum:
    monitor_id = "page_cusum"

    def __init__(self, *, reference_mean: float, threshold: float) -> None:
        self._reference_mean = reference_mean
        self._threshold = threshold
        self._step = 0
        self._statistic = 0.0
        self._maximum = 0.0

    def update(self, score: float) -> MonitorSnapshot:
        self._statistic = max(
            0.0, self._statistic + score - self._reference_mean
        )
        self._maximum = max(self._maximum, self._statistic)
        snapshot = MonitorSnapshot(
            step=self._step,
            statistic=self._statistic,
            max_statistic=self._maximum,
            alarm=self._maximum > self._threshold,
        )
        self._step += 1
        return snapshot


def run_monitor(
    monitor: StreamingMonitor,
    scores: Iterable[float],
) -> MonitorRun:
    alarm_step = None
    last = None
    for score in scores:
        last = monitor.update(score)
        if last.alarm and alarm_step is None:
            alarm_step = last.step
    if last is None:
        raise ValueError("a monitor run requires at least one score")
    return MonitorRun(
        alarm_step=alarm_step,
        terminal_statistic=last.statistic,
        max_statistic=last.max_statistic,
    )
