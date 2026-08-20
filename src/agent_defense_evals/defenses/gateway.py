"""Complete-mediation point for proposed agent actions."""

from typing import Any

from agent_defense_evals.core.schemas import (
    AgentAction,
    DecisionKind,
    DefenseDecision,
)
from agent_defense_evals.defenses.base import Defense


class DefenseGateway:
    def __init__(self, defenses: tuple[Defense, ...]) -> None:
        self.defenses = defenses

    def evaluate(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> tuple[DefenseDecision, ...]:
        current = action
        decisions: list[DefenseDecision] = []
        if not self.defenses:
            return (
                DefenseDecision(
                    decision=DecisionKind.ALLOW,
                    defense_id="gateway.default",
                    action=current,
                    reason="no configured defense blocked the action",
                ),
            )
        for defense in self.defenses:
            decision = defense.evaluate(
                current, step=step, scenario_state=scenario_state
            )
            decisions.append(decision)
            current = decision.action
            if decision.decision is DecisionKind.BLOCK:
                break
        return tuple(decisions)
