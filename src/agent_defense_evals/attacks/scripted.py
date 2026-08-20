"""Deterministic attacks used to verify the common action path."""

from typing import Any

from agent_defense_evals.core.schemas import ActionKind, AgentAction


class NoAttack:
    attack_id = "none"

    def transform_action(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> AgentAction:
        del step, scenario_state
        return action


class ForceSelectionAttack:
    attack_id = "force_selection"

    def __init__(self, *, target_agent: str, forced_plan: str) -> None:
        self.target_agent = target_agent
        self.forced_plan = forced_plan

    def transform_action(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> AgentAction:
        del step, scenario_state
        if (
            action.actor_id == self.target_agent
            and action.kind is ActionKind.SELECT_PLAN
        ):
            return action.model_copy(update={"payload": {"plan_id": self.forced_plan}})
        return action
