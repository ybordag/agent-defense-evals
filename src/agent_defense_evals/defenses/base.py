"""Defense contract."""

from typing import Any, Protocol

from agent_defense_evals.core.schemas import AgentAction, DefenseDecision


class Defense(Protocol):
    defense_id: str

    def evaluate(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> DefenseDecision: ...
