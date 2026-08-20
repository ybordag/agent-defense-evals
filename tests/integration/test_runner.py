from pathlib import Path

from agent_defense_evals.cli import build_runner
from agent_defense_evals.core.config import load_experiment
from agent_defense_evals.core.factory import (
    build_agents,
    build_attack,
    build_scenario,
)
from agent_defense_evals.core.runner import ExperimentRunner
from agent_defense_evals.core.schemas import DecisionKind, EventKind
from agent_defense_evals.defenses.gateway import DefenseGateway

BASELINE = Path("configs/experiments/scripted_baseline.yaml")
BLOCKED = Path("configs/experiments/scripted_blocked_attack.yaml")


def test_benign_agents_combine_private_constraints() -> None:
    result, trace = build_runner(BASELINE).run()

    assert result.selected_plan == "beta"
    assert result.utility.success
    assert not result.security.violation
    assert len(trace.by_kind(EventKind.EPISODE_COMPLETED)) == 1


def test_blocked_attack_cannot_change_environment() -> None:
    result, trace = build_runner(BLOCKED).run()
    decisions = trace.by_kind(EventKind.DEFENSE_DECIDED)
    blocked = [
        event
        for event in decisions
        if event.payload["decision"]["decision"] == DecisionKind.BLOCK.value
    ]
    applied_forced = [
        event
        for event in trace.by_kind(EventKind.ACTION_APPLIED)
        if event.payload["action"].get("payload", {}).get("plan_id") == "alpha"
    ]

    assert trace.by_kind(EventKind.ATTACK_MUTATED)
    assert blocked
    assert not applied_forced
    assert result.selected_plan is None
    assert not result.security.violation


def test_unblocked_attack_reaches_same_scenario_interface() -> None:
    spec = load_experiment(BLOCKED)
    scenario = build_scenario(spec)
    runner = ExperimentRunner(
        spec=spec.model_copy(update={"defenses": ()}),
        scenario=scenario,
        agents=build_agents(spec),
        attack=build_attack(spec),
        gateway=DefenseGateway(()),
    )

    result, _ = runner.run()

    assert result.selected_plan == "alpha"
    assert result.security.violation
    assert not result.utility.success
