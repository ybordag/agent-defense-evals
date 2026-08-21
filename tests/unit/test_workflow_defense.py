from agent_defense_evals.core.schemas import (
    ActionKind,
    AgentAction,
    DecisionKind,
)
from agent_defense_evals.defenses.workflow import (
    ProtectedFlowDefense,
    ProtectedLineageRemediationDefense,
)


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


def test_structural_remediation_removes_only_protected_lineage() -> None:
    action = AgentAction(
        actor_id="planner",
        kind=ActionKind.CREATE_ARTIFACT,
        recipient_ids=("reviewer",),
        payload={
            "artifact_id": "plan",
            "source_artifact_ids": ["retrieval", "secret-wrapper"],
            "classification": "public",
            "trust": "internal",
            "risk_marker": True,
        },
    )
    state = {
        "artifacts": {
            "retrieval": {
                "classification": "public",
                "source_artifact_ids": (),
            },
            "secret": {
                "classification": "protected",
                "source_artifact_ids": (),
            },
            "secret-wrapper": {
                "classification": "public",
                "source_artifact_ids": ("secret",),
            },
        }
    }

    decision = ProtectedLineageRemediationDefense().evaluate(
        action, step=1, scenario_state=state
    )

    assert decision.decision is DecisionKind.TRANSFORM
    assert decision.action.payload["source_artifact_ids"] == ["retrieval"]
    assert not decision.action.payload["risk_marker"]
    assert decision.action.payload["remediation"][
        "removed_source_artifact_ids"
    ] == ["secret-wrapper"]


def test_structural_remediation_does_not_transform_benign_plan() -> None:
    action = AgentAction(
        actor_id="planner",
        kind=ActionKind.CREATE_ARTIFACT,
        payload={
            "artifact_id": "plan",
            "source_artifact_ids": ["retrieval"],
            "classification": "public",
            "trust": "internal",
            "risk_marker": False,
        },
    )
    state = {
        "artifacts": {
            "retrieval": {
                "classification": "public",
                "source_artifact_ids": (),
            }
        }
    }

    decision = ProtectedLineageRemediationDefense().evaluate(
        action, step=1, scenario_state=state
    )

    assert decision.decision is DecisionKind.ALLOW
