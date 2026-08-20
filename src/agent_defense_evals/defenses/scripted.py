"""Deterministic defense used to verify gateway enforcement."""

from typing import Any

from agent_defense_evals.core.schemas import (
    ActionKind,
    AgentAction,
    DecisionKind,
    DefenseDecision,
)


class BlockPlanDefense:
    defense_id = "block_plan"

    def __init__(self, blocked_plans: tuple[str, ...]) -> None:
        self.blocked_plans = frozenset(blocked_plans)

    def evaluate(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> DefenseDecision:
        del step, scenario_state
        blocked = (
            action.kind is ActionKind.SELECT_PLAN
            and str(action.payload["plan_id"]) in self.blocked_plans
        )
        return DefenseDecision(
            decision=DecisionKind.BLOCK if blocked else DecisionKind.ALLOW,
            defense_id=self.defense_id,
            action=action,
            reason="plan is blocked" if blocked else "plan is permitted",
        )


class RewritePlanDefense:
    defense_id = "rewrite_plan"

    def __init__(self, *, source_plan: str, replacement_plan: str) -> None:
        self.source_plan = source_plan
        self.replacement_plan = replacement_plan

    def evaluate(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> DefenseDecision:
        del step, scenario_state
        should_rewrite = (
            action.kind is ActionKind.SELECT_PLAN
            and str(action.payload["plan_id"]) == self.source_plan
        )
        transformed = (
            action.model_copy(update={"payload": {"plan_id": self.replacement_plan}})
            if should_rewrite
            else action
        )
        return DefenseDecision(
            decision=DecisionKind.TRANSFORM if should_rewrite else DecisionKind.ALLOW,
            defense_id=self.defense_id,
            action=transformed,
            reason="plan rewritten" if should_rewrite else "no rewrite required",
        )
