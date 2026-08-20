"""Deterministic policies used to verify the orchestration contracts."""

from agent_defense_evals.core.schemas import ActionKind, AgentAction, Observation


class ConstraintSharingAgent:
    def __init__(self, agent_id: str, *, coordinator: bool) -> None:
        self.agent_id = agent_id
        self.coordinator = coordinator

    def act(self, observation: Observation) -> AgentAction:
        if observation.step == 0:
            return AgentAction(
                actor_id=self.agent_id,
                kind=ActionKind.MESSAGE,
                recipient_ids=tuple(observation.public_state["other_agents"]),
                payload={
                    "allowed_plans": list(observation.private_state["allowed_plans"])
                },
            )

        if self.coordinator and observation.public_state["selected_plan"] is None:
            feasible = set(observation.private_state["allowed_plans"])
            for message in observation.inbox:
                feasible.intersection_update(message["payload"]["allowed_plans"])
            scores = observation.public_state["scores"]
            if not feasible:
                return AgentAction(actor_id=self.agent_id, kind=ActionKind.NOOP)
            selected = max(feasible, key=lambda plan_id: (scores[plan_id], plan_id))
            return AgentAction(
                actor_id=self.agent_id,
                kind=ActionKind.SELECT_PLAN,
                payload={"plan_id": selected},
            )

        return AgentAction(actor_id=self.agent_id, kind=ActionKind.NOOP)
