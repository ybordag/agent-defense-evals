from agent_defense_evals.core.schemas import (
    ActionKind,
    AgentAction,
    DecisionKind,
)
from agent_defense_evals.defenses.workflow import ProtectedFlowDefense


def test_protected_flow_gate_blocks_transitive_external_execution() -> None:
    action = AgentAction(
        actor_id="executor",
        kind=ActionKind.EXECUTE_ARTIFACT,
        payload={"artifact_id": "plan", "sink": "external"},
    )
    state = {
        "artifacts": {
            "secret": {
                "classification": "protected",
                "source_artifact_ids": (),
            },
            "plan": {
                "classification": "public",
                "source_artifact_ids": ("secret",),
            },
        }
    }

    decision = ProtectedFlowDefense().evaluate(
        action,
        step=4,
        scenario_state=state,
    )

    assert decision.decision is DecisionKind.BLOCK
