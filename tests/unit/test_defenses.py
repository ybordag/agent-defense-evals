from agent_defense_evals.core.schemas import ActionKind, AgentAction, DecisionKind
from agent_defense_evals.defenses.gateway import DefenseGateway
from agent_defense_evals.defenses.scripted import RewritePlanDefense


def test_gateway_propagates_transformed_action() -> None:
    action = AgentAction(
        actor_id="coordinator",
        kind=ActionKind.SELECT_PLAN,
        payload={"plan_id": "alpha"},
    )
    gateway = DefenseGateway(
        (
            RewritePlanDefense(
                source_plan="alpha",
                replacement_plan="beta",
            ),
        )
    )

    decisions = gateway.evaluate(action, step=1, scenario_state={})

    assert decisions[-1].decision is DecisionKind.TRANSFORM
    assert decisions[-1].action.payload["plan_id"] == "beta"
