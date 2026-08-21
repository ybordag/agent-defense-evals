from pathlib import Path

import pytest

from agent_defense_evals.core.config import load_experiment
from agent_defense_evals.core.factory import build_defenses
from agent_defense_evals.core.schemas import (
    ActionKind,
    AgentAction,
    ComponentSpec,
    DecisionKind,
)
from agent_defense_evals.defenses.mediation import (
    MediatorKind,
    MemoryMode,
    MessageMediatorDefense,
    ReceiverMemoryCompartment,
)


def _message() -> AgentAction:
    return AgentAction(
        actor_id="sender",
        kind=ActionKind.MESSAGE,
        recipient_ids=("receiver",),
        payload={
            "task_id": "release-check",
            "surface_code": 3,
            "semantic_code": 3,
            "round": 0,
        },
    )


def _apply(kind: MediatorKind, *, seed: int = 17) -> AgentAction:
    decision = MessageMediatorDefense(
        kind,
        base_seed=11,
        information_budget_bits=1,
        randomized_retention=0.5,
    ).evaluate(_message(), step=0, scenario_state={"episode_seed": seed})
    assert decision.decision is DecisionKind.TRANSFORM
    return decision.action


def test_mediators_preserve_task_and_shape_carriers() -> None:
    unrestricted = _apply(MediatorKind.UNRESTRICTED).payload
    paraphrased = _apply(MediatorKind.GENERIC_PARAPHRASE).payload
    typed = _apply(MediatorKind.TYPED_SCHEMA).payload
    summarized = _apply(MediatorKind.TASK_SUMMARY).payload
    budgeted = _apply(MediatorKind.INFORMATION_BUDGET).payload

    assert unrestricted["surface_code"] == 3
    assert unrestricted["semantic_code"] == 3
    assert paraphrased["surface_code"] == 0
    assert paraphrased["semantic_code"] == 3
    assert typed["surface_code"] == typed["semantic_code"] == 0
    assert summarized["surface_code"] == summarized["semantic_code"] == 0
    assert budgeted["surface_code"] == 0
    assert budgeted["semantic_code"] == 1
    assert {
        payload["task_id"]
        for payload in (unrestricted, paraphrased, typed, summarized, budgeted)
    } == {"release-check"}


def test_recipient_randomization_is_seeded_and_nonconstant() -> None:
    mediator = MessageMediatorDefense(
        MediatorKind.RECIPIENT_RANDOMIZED,
        base_seed=11,
        randomized_retention=0.5,
    )

    def output(seed: int) -> int:
        return int(
            mediator.evaluate(
                _message(), step=0, scenario_state={"episode_seed": seed}
            ).action.payload["semantic_code"]
        )

    assert output(5) == output(5)
    assert {output(seed) for seed in range(32)} == {0, 3}


def test_mediator_rejects_untyped_messages_and_allows_other_actions() -> None:
    mediator = MessageMediatorDefense(MediatorKind.TYPED_SCHEMA, base_seed=1)
    with pytest.raises(ValueError, match="missing fields"):
        mediator.evaluate(
            AgentAction(
                actor_id="sender",
                kind=ActionKind.MESSAGE,
                recipient_ids=("receiver",),
                payload={"text": "untyped"},
            ),
            step=0,
            scenario_state={"episode_seed": 1},
        )
    noop = AgentAction(actor_id="sender", kind=ActionKind.NOOP)
    decision = mediator.evaluate(noop, step=0, scenario_state={"episode_seed": 1})
    assert decision.decision is DecisionKind.ALLOW
    assert decision.action == noop


def test_memory_compartment_removes_cross_turn_history() -> None:
    history = ("first-bit", "second-bit")
    assert ReceiverMemoryCompartment(MemoryMode.CUMULATIVE).view(history) == history
    assert ReceiverMemoryCompartment(MemoryMode.RESET_EACH_TURN).view(history) == (
        "second-bit",
    )


def test_mediator_builds_through_common_defense_factory() -> None:
    base = load_experiment(Path("configs/experiments/scripted_baseline.yaml"))
    spec = base.model_copy(
        update={
            "defenses": (
                ComponentSpec(
                    kind="message_mediator",
                    config={"mediator": "typed_schema"},
                ),
            )
        }
    )
    defenses = build_defenses(spec)

    assert len(defenses) == 1
    assert isinstance(defenses[0], MessageMediatorDefense)
    assert defenses[0].kind is MediatorKind.TYPED_SCHEMA
