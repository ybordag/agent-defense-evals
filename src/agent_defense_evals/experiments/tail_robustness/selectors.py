"""Validation-only defense-stack selectors."""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Iterable

from agent_defense_evals.experiments.tail_robustness.contracts import (
    TailExperimentSpec,
    TailStackSpec,
    TailTrajectoryOutcome,
)
from agent_defense_evals.experiments.tail_robustness.statistics import (
    dkw_cvar_ucb,
    upper_tail_cvar,
)

SELECTOR_NAMES = (
    "pooled_mean",
    "pooled_cvar",
    "worst_cell_mean",
    "hierarchical_tail",
    "ucb_tail",
)


def _by_cell(
    outcomes: Iterable[TailTrajectoryOutcome],
) -> dict[str, list[TailTrajectoryOutcome]]:
    grouped: dict[str, list[TailTrajectoryOutcome]] = defaultdict(list)
    for outcome in outcomes:
        grouped[outcome.cell_id].append(outcome)
    return dict(grouped)


def _feasible(
    spec: TailExperimentSpec,
    outcomes: list[TailTrajectoryOutcome],
) -> bool:
    benign = [item for item in outcomes if item.component_bypass == {}]
    false_alarm = (
        sum(item.false_alarm for item in benign) / len(benign) if benign else 0.0
    )
    return (
        statistics.fmean(item.utility for item in outcomes) >= spec.utility_floor
        and statistics.fmean(item.latency_ms for item in outcomes)
        <= spec.latency_ceiling_ms
        and false_alarm <= spec.false_alarm_ceiling
    )


def selector_objective(
    name: str,
    spec: TailExperimentSpec,
    outcomes: list[TailTrajectoryOutcome],
) -> float:
    """Evaluate one registered selector objective on one stack."""

    losses = [item.security_loss for item in outcomes]
    cells = _by_cell(outcomes)
    if name == "pooled_mean":
        return statistics.fmean(losses)
    if name == "pooled_cvar":
        return upper_tail_cvar(losses, spec.tail_fraction)
    if name == "worst_cell_mean":
        return max(
            statistics.fmean(item.security_loss for item in cell)
            for cell in cells.values()
        )
    if name == "hierarchical_tail":
        return max(
            upper_tail_cvar(
                (item.security_loss for item in cell), spec.tail_fraction
            )
            for cell in cells.values()
        )
    if name == "ucb_tail":
        per_cell_delta = spec.confidence_delta / max(1, len(cells))
        return max(
            dkw_cvar_ucb(
                (item.security_loss for item in cell),
                spec.tail_fraction,
                per_cell_delta,
            )
            for cell in cells.values()
        )
    raise ValueError(f"unknown selector: {name}")


def select_stacks(
    spec: TailExperimentSpec,
    validation_outcomes: tuple[TailTrajectoryOutcome, ...],
) -> dict[str, str]:
    """Run all five selectors using validation outcomes only."""

    registered = {item.stack_id: item for item in spec.stacks}
    grouped: dict[str, list[TailTrajectoryOutcome]] = defaultdict(list)
    for outcome in validation_outcomes:
        if outcome.split.value != "validation":
            raise ValueError("stack selection accepts validation outcomes only")
        if outcome.stack_id not in registered:
            raise ValueError(f"unregistered stack in outcomes: {outcome.stack_id}")
        grouped[outcome.stack_id].append(outcome)
    if set(grouped) != set(registered):
        raise ValueError("validation outcomes must cover every registered stack")

    eligible = {
        stack_id: items
        for stack_id, items in grouped.items()
        if _feasible(spec, items)
    }
    if not eligible:
        raise ValueError("no stack satisfies validation operational constraints")

    def cost(stack: TailStackSpec) -> tuple[float, str]:
        return (stack.latency_ms, stack.stack_id)

    selected: dict[str, str] = {}
    for name in SELECTOR_NAMES:
        selected[name] = min(
            eligible,
            key=lambda stack_id: (
                selector_objective(name, spec, eligible[stack_id]),
                selector_objective(
                    "hierarchical_tail", spec, eligible[stack_id]
                ),
                selector_objective("pooled_mean", spec, eligible[stack_id]),
                cost(registered[stack_id]),
            ),
        )
    return selected
