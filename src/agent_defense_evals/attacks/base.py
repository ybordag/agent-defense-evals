"""Attack strategy contract."""

from typing import Any, Protocol

from agent_defense_evals.core.schemas import AgentAction


class AttackStrategy(Protocol):
    attack_id: str

    def transform_action(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> AgentAction: ...
